"""
Booking service for managing reservations.
Handles the complete booking flow with transactional integrity.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.booking import Booking, BookingStatus
from app.models.customer import Customer
from app.models.room_type import RoomType
from app.schemas.booking import BookingCreate, BookingRead
from app.services.inventory_service import check_availability, deduct_inventory, restore_inventory
from app.utils.date_utils import validate_date_range


async def get_or_create_customer(
    db: AsyncSession,
    name: str,
    email: str,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    id_proof_type: Optional[str] = None,
    id_proof_number: Optional[str] = None
) -> Customer:
    """
    Get existing customer by email or create a new one.
    
    Args:
        db: Database session
        name: Customer name
        email: Customer email (unique identifier)
        phone: Optional phone number
        address: Optional address
        id_proof_type: Optional ID proof type
        id_proof_number: Optional ID proof number
    
    Returns:
        Customer model instance
    """
    # Try to find existing customer
    result = await db.execute(
        select(Customer).where(Customer.email == email)
    )
    customer = result.scalar_one_or_none()
    
    if customer:
        # Update customer info if provided
        customer.name = name
        if phone:
            customer.phone = phone
        if address:
            customer.address = address
        if id_proof_type:
            customer.id_proof_type = id_proof_type
        if id_proof_number:
            customer.id_proof_number = id_proof_number
        return customer
    
    # Create new customer
    customer = Customer(
        name=name,
        email=email,
        phone=phone,
        address=address,
        id_proof_type=id_proof_type,
        id_proof_number=id_proof_number
    )
    db.add(customer)
    await db.flush()  # Get the ID without committing
    
    return customer


async def create_booking(
    db: AsyncSession,
    booking_data: BookingCreate
) -> Booking:
    """
    Create a new booking with full validation and inventory management.
    This is a transactional operation - all or nothing.
    
    Flow:
    1. Validate date range
    2. Check room type exists
    3. Check inventory availability
    4. Get or create customer
    5. Deduct inventory
    6. Create booking record
    
    Args:
        db: Database session
        booking_data: Booking creation schema
    
    Returns:
        Created Booking model instance
    
    Raises:
        HTTPException: If validation fails or no availability
    """
    try:
        # 1. Validate date range
        validate_date_range(booking_data.check_in, booking_data.check_out)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # 2. Check room type exists
    result = await db.execute(
        select(RoomType).where(RoomType.id == booking_data.room_type_id)
    )
    room_type = result.scalar_one_or_none()
    
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with ID {booking_data.room_type_id} not found"
        )
    
    # 3. Check availability
    is_available, _, error_message = await check_availability(
        db,
        booking_data.room_type_id,
        booking_data.check_in,
        booking_data.check_out,
        booking_data.num_rooms
    )
    
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_message
        )
    
    # Start transaction (everything from here should be atomic)
    try:
        # 4. Get or create customer
        customer = await get_or_create_customer(
            db,
            name=booking_data.customer.name,
            email=booking_data.customer.email,
            phone=booking_data.customer.phone,
            address=booking_data.customer.address,
            id_proof_type=booking_data.customer.id_proof_type,
            id_proof_number=booking_data.customer.id_proof_number
        )
        
        # 5. Deduct inventory (this will raise if not available)
        total_amount = await deduct_inventory(
            db,
            booking_data.room_type_id,
            booking_data.check_in,
            booking_data.check_out,
            booking_data.num_rooms
        )
        
        # 6. Create booking record
        booking = Booking(
            customer_id=customer.id,
            room_type_id=booking_data.room_type_id,
            check_in=booking_data.check_in,
            check_out=booking_data.check_out,
            num_rooms=booking_data.num_rooms,
            total_amount=total_amount,
            amount_paid=booking_data.amount_paid,
            status=BookingStatus.CONFIRMED.value,
            notes=booking_data.notes
        )
        db.add(booking)
        
        # Commit the transaction
        await db.commit()
        await db.refresh(booking)
        
        return booking
        
    except HTTPException:
        # Re-raise HTTP exceptions
        await db.rollback()
        raise
    except Exception as e:
        # Rollback on any other error
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Booking failed: {str(e)}"
        )


async def cancel_booking(
    db: AsyncSession,
    booking_id: int,
    reason: Optional[str] = None
) -> Booking:
    """
    Cancel a booking and restore inventory.
    
    Args:
        db: Database session
        booking_id: ID of the booking to cancel
        reason: Optional cancellation reason
    
    Returns:
        Updated Booking model instance
    
    Raises:
        HTTPException: If booking not found or already cancelled
    """
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    if booking.status == BookingStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    try:
        # Restore inventory
        await restore_inventory(
            db,
            booking.room_type_id,
            booking.check_in,
            booking.check_out,
            booking.num_rooms
        )
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED.value
        if reason:
            booking.notes = f"{booking.notes or ''}\nCancellation reason: {reason}".strip()
        
        await db.commit()
        await db.refresh(booking)
        
        return booking
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cancellation failed: {str(e)}"
        )


async def get_booking_by_id(
    db: AsyncSession,
    booking_id: int
) -> Optional[Booking]:
    """
    Get a booking by its ID.
    
    Args:
        db: Database session
        booking_id: Booking ID
    
    Returns:
        Booking model instance or None
    """
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    return result.scalar_one_or_none()


def booking_to_read_schema(booking: Booking) -> BookingRead:
    """
    Convert a Booking model to BookingRead schema.
    
    Args:
        booking: Booking model instance
    
    Returns:
        BookingRead schema
    """
    return BookingRead(
        id=booking.id,
        customer_id=booking.customer_id,
        customer_name=booking.customer.name,
        customer_email=booking.customer.email,
        room_type_id=booking.room_type_id,
        room_type_name=booking.room_type.name,
        check_in=booking.check_in,
        check_out=booking.check_out,
        num_rooms=booking.num_rooms,
        total_amount=booking.total_amount,
        amount_paid=booking.amount_paid,
        balance_due=booking.balance_due,
        status=booking.status,
        notes=booking.notes,
        created_at=booking.created_at
    )

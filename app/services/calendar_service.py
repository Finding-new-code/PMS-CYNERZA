"""
Calendar service for generating frontend-ready calendar data.

Responsibilities:
- Fetch inventory data by date range (efficient single query)
- Join with room types for display names
- Calculate availability status
- Transform bookings into calendar event blocks
"""

from datetime import date
from typing import List, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.inventory import Inventory
from app.models.room_type import RoomType
from app.models.booking import Booking, BookingStatus
from app.schemas.calendar import CalendarAvailability, BookingEvent, CalendarSummary
from app.core.exceptions import InvalidDateRangeError


def calculate_status(available_rooms: int, total_rooms: int) -> str:
    """
    Calculate availability status for a cell.
    
    Args:
        available_rooms: Currently available rooms
        total_rooms: Total rooms of this type
    
    Returns:
        Status string: "available", "partial", or "full"
    """
    if available_rooms == total_rooms:
        return "available"
    elif available_rooms > 0:
        return "partial"
    else:
        return "full"


async def get_availability_grid(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    room_type_id: int = None
) -> List[CalendarAvailability]:
    """
    Get availability grid data for the calendar view.
    Returns one entry per room type per date.
    
    Uses efficient JOINs to avoid N+1 queries.
    
    Args:
        db: Database session
        start_date: Start date (inclusive)
        end_date: End date (inclusive for display, exclusive in query)
        room_type_id: Optional filter for specific room type
    
    Returns:
        List of CalendarAvailability objects
    """
    if end_date <= start_date:
        raise InvalidDateRangeError("End date must be after start date")
    
    # Build query with JOIN to room_types
    query = (
        select(Inventory, RoomType)
        .join(RoomType, Inventory.room_type_id == RoomType.id)
        .where(
            and_(
                Inventory.date >= start_date,
                Inventory.date < end_date
            )
        )
        .order_by(Inventory.date, RoomType.name)
    )
    
    if room_type_id:
        query = query.where(Inventory.room_type_id == room_type_id)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Transform to response schema
    availability_grid = []
    for inventory, room_type in rows:
        status = calculate_status(inventory.available_rooms, room_type.total_rooms)
        
        availability_grid.append(CalendarAvailability(
            date=inventory.date,
            room_type_id=room_type.id,
            room_type_name=room_type.name,
            available_rooms=inventory.available_rooms,
            total_rooms=room_type.total_rooms,
            price=inventory.price,
            status=status
        ))
    
    return availability_grid


async def get_booking_events(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    room_type_id: int = None,
    include_cancelled: bool = False
) -> List[BookingEvent]:
    """
    Get bookings as calendar event blocks.
    Returns bookings that overlap with the date range.
    
    A booking overlaps if:
    - check_in < end_date AND check_out > start_date
    
    Args:
        db: Database session
        start_date: Start date of calendar view
        end_date: End date of calendar view
        room_type_id: Optional filter for specific room type
        include_cancelled: Whether to include cancelled bookings
    
    Returns:
        List of BookingEvent objects
    """
    if end_date <= start_date:
        raise InvalidDateRangeError("End date must be after start date")
    
    # Build query with JOINs
    query = (
        select(Booking)
        .options(
            selectinload(Booking.room_type),
            selectinload(Booking.customer)
        )
        .where(
            and_(
                # Booking overlaps with date range
                Booking.check_in < end_date,
                Booking.check_out > start_date
            )
        )
        .order_by(Booking.check_in)
    )
    
    if room_type_id:
        query = query.where(Booking.room_type_id == room_type_id)
    
    if not include_cancelled:
        query = query.where(Booking.status != BookingStatus.CANCELLED.value)
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    # Transform to calendar events
    events = []
    for booking in bookings:
        title = f"{booking.room_type.name} - {booking.customer.name}"
        
        events.append(BookingEvent(
            booking_id=booking.id,
            title=title,
            room_type_id=booking.room_type_id,
            room_type_name=booking.room_type.name,
            customer_name=booking.customer.name,
            start=booking.check_in,
            end=booking.check_out,
            num_rooms=booking.num_rooms,
            status=booking.status
        ))
    
    return events


async def get_calendar_summary(
    db: AsyncSession,
    start_date: date,
    end_date: date
) -> CalendarSummary:
    """
    Get summary statistics for a date range.
    
    Args:
        db: Database session
        start_date: Start date
        end_date: End date
    
    Returns:
        CalendarSummary with aggregated stats
    """
    if end_date <= start_date:
        raise InvalidDateRangeError("End date must be after start date")
    
    # Get all bookings in range (excluding cancelled)
    query = (
        select(Booking)
        .where(
            and_(
                Booking.check_in < end_date,
                Booking.check_out > start_date,
                Booking.status != BookingStatus.CANCELLED.value
            )
        )
    )
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    total_bookings = len(bookings)
    total_rooms_booked = sum(b.num_rooms for b in bookings)
    
    # Calculate occupancy (simplified - based on inventory)
    inventory_query = (
        select(Inventory, RoomType)
        .join(RoomType, Inventory.room_type_id == RoomType.id)
        .where(
            and_(
                Inventory.date >= start_date,
                Inventory.date < end_date
            )
        )
    )
    
    inv_result = await db.execute(inventory_query)
    inventory_rows = inv_result.all()
    
    total_capacity = sum(rt.total_rooms for _, rt in inventory_rows)
    total_available = sum(inv.available_rooms for inv, _ in inventory_rows)
    
    if total_capacity > 0:
        occupancy = ((total_capacity - total_available) / total_capacity) * 100
    else:
        occupancy = 0.0
    
    return CalendarSummary(
        start_date=start_date,
        end_date=end_date,
        total_bookings=total_bookings,
        total_rooms_booked=total_rooms_booked,
        occupancy_percentage=round(occupancy, 2)
    )

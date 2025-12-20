"""
Inventory service for managing date-wise room availability.
Handles inventory generation, availability checks, and atomic updates.
"""

from datetime import date, timedelta
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.inventory import Inventory
from app.models.room_type import RoomType
from app.schemas.inventory import InventoryAvailability, DateRangeAvailability
from app.utils.date_utils import get_date_list, get_future_dates
from app.core.config import get_settings

settings = get_settings()


async def generate_inventory_for_room_type(
    db: AsyncSession,
    room_type: RoomType,
    days_ahead: int = None
) -> int:
    """
    Generate inventory records for a room type for the next N days.
    Skips dates that already have inventory records.
    
    Args:
        db: Database session
        room_type: RoomType model instance
        days_ahead: Number of days to generate (defaults to config value)
    
    Returns:
        Number of inventory records created
    """
    if days_ahead is None:
        days_ahead = settings.INVENTORY_DAYS_AHEAD
    
    dates = get_future_dates(days_ahead)
    created_count = 0
    
    for inv_date in dates:
        # Check if inventory already exists for this date
        existing = await db.execute(
            select(Inventory).where(
                and_(
                    Inventory.room_type_id == room_type.id,
                    Inventory.date == inv_date
                )
            )
        )
        
        if existing.scalar_one_or_none() is None:
            inventory = Inventory(
                room_type_id=room_type.id,
                date=inv_date,
                available_rooms=room_type.total_rooms,
                price=room_type.base_price
            )
            db.add(inventory)
            created_count += 1
    
    await db.commit()
    return created_count


async def get_inventory_for_date_range(
    db: AsyncSession,
    room_type_id: int,
    start_date: date,
    end_date: date
) -> List[Inventory]:
    """
    Get inventory records for a room type within a date range.
    
    Args:
        db: Database session
        room_type_id: ID of the room type
        start_date: Start date (inclusive)
        end_date: End date (exclusive, check-out date)
    
    Returns:
        List of Inventory records
    """
    result = await db.execute(
        select(Inventory)
        .where(
            and_(
                Inventory.room_type_id == room_type_id,
                Inventory.date >= start_date,
                Inventory.date < end_date
            )
        )
        .order_by(Inventory.date)
    )
    return list(result.scalars().all())


async def check_availability(
    db: AsyncSession,
    room_type_id: int,
    check_in: date,
    check_out: date,
    num_rooms: int = 1
) -> tuple[bool, List[Inventory], Optional[str]]:
    """
    Check if rooms are available for all dates in the range.
    
    Args:
        db: Database session
        room_type_id: ID of the room type
        check_in: Check-in date
        check_out: Check-out date
        num_rooms: Number of rooms needed
    
    Returns:
        Tuple of (is_available, inventory_records, error_message)
    """
    required_dates = get_date_list(check_in, check_out)
    inventory_records = await get_inventory_for_date_range(
        db, room_type_id, check_in, check_out
    )
    
    # Check if we have inventory for all required dates
    inventory_dates = {inv.date for inv in inventory_records}
    missing_dates = [d for d in required_dates if d not in inventory_dates]
    
    if missing_dates:
        return False, [], f"No inventory for dates: {missing_dates[0]} - {missing_dates[-1]}"
    
    # Check availability for each date
    for inv in inventory_records:
        if inv.available_rooms < num_rooms:
            return False, inventory_records, f"Only {inv.available_rooms} room(s) available on {inv.date}"
    
    return True, inventory_records, None


async def deduct_inventory(
    db: AsyncSession,
    room_type_id: int,
    check_in: date,
    check_out: date,
    num_rooms: int = 1
) -> Decimal:
    """
    Atomically deduct inventory for a booking.
    This should be called within a transaction.
    
    Args:
        db: Database session (should be in a transaction)
        room_type_id: ID of the room type
        check_in: Check-in date
        check_out: Check-out date
        num_rooms: Number of rooms to deduct
    
    Returns:
        Total price for the booking
    
    Raises:
        HTTPException: If rooms are not available
    """
    # Get inventory with row-level lock (FOR UPDATE)
    # Note: SQLite doesn't support FOR UPDATE, but PostgreSQL does
    required_dates = get_date_list(check_in, check_out)
    total_price = Decimal("0.00")
    
    for booking_date in required_dates:
        # For SQLite compatibility, we just select; for PostgreSQL, use with_for_update()
        result = await db.execute(
            select(Inventory)
            .where(
                and_(
                    Inventory.room_type_id == room_type_id,
                    Inventory.date == booking_date
                )
            )
            .with_for_update()  # Row-level lock for PostgreSQL
        )
        inventory = result.scalar_one_or_none()
        
        if inventory is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No inventory available for {booking_date}"
            )
        
        if inventory.available_rooms < num_rooms:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Only {inventory.available_rooms} room(s) available on {booking_date}. "
                       f"Requested: {num_rooms}"
            )
        
        # Deduct rooms
        inventory.available_rooms -= num_rooms
        total_price += inventory.price * num_rooms
    
    return total_price


async def restore_inventory(
    db: AsyncSession,
    room_type_id: int,
    check_in: date,
    check_out: date,
    num_rooms: int = 1
) -> None:
    """
    Restore inventory when a booking is cancelled.
    
    Args:
        db: Database session
        room_type_id: ID of the room type
        check_in: Check-in date
        check_out: Check-out date
        num_rooms: Number of rooms to restore
    """
    required_dates = get_date_list(check_in, check_out)
    
    for booking_date in required_dates:
        result = await db.execute(
            select(Inventory)
            .where(
                and_(
                    Inventory.room_type_id == room_type_id,
                    Inventory.date == booking_date
                )
            )
        )
        inventory = result.scalar_one_or_none()
        
        if inventory:
            inventory.available_rooms += num_rooms


async def get_availability_summary(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    room_type_id: Optional[int] = None
) -> List[DateRangeAvailability]:
    """
    Get availability summary for all room types (or a specific one).
    
    Args:
        db: Database session
        start_date: Start date
        end_date: End date
        room_type_id: Optional room type filter
    
    Returns:
        List of availability summaries
    """
    # Get room types
    query = select(RoomType)
    if room_type_id:
        query = query.where(RoomType.id == room_type_id)
    
    result = await db.execute(query)
    room_types = result.scalars().all()
    
    summaries = []
    
    for rt in room_types:
        inventory_records = await get_inventory_for_date_range(
            db, rt.id, start_date, end_date
        )
        
        if not inventory_records:
            continue
        
        daily_breakdown = [
            InventoryAvailability(
                room_type_id=rt.id,
                room_type_name=rt.name,
                date=inv.date,
                available_rooms=inv.available_rooms,
                price=inv.price
            )
            for inv in inventory_records
        ]
        
        min_available = min(inv.available_rooms for inv in inventory_records)
        total_price = sum(inv.price for inv in inventory_records)
        
        summaries.append(DateRangeAvailability(
            room_type_id=rt.id,
            room_type_name=rt.name,
            start_date=start_date,
            end_date=end_date,
            min_available=min_available,
            total_price=total_price,
            daily_breakdown=daily_breakdown
        ))
    
    return summaries

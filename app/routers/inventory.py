"""
Inventory management router.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.inventory import Inventory
from app.models.room_type import RoomType
from app.schemas.inventory import InventoryRead, InventoryUpdate, DateRangeAvailability
from app.services.inventory_service import get_availability_summary, generate_inventory_for_room_type

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=List[DateRangeAvailability])
async def get_inventory(
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    room_type_id: Optional[int] = Query(None, description="Filter by room type ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get inventory availability for a date range.
    
    Returns availability summary for all room types (or a specific one).
    
    - **start**: Start date (inclusive)
    - **end**: End date (exclusive, check-out date)
    - **room_type_id**: Optional filter for specific room type
    """
    if end <= start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    return await get_availability_summary(db, start, end, room_type_id)


@router.get("/detailed", response_model=List[InventoryRead])
async def get_detailed_inventory(
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    room_type_id: Optional[int] = Query(None, description="Filter by room type ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed daily inventory records.
    
    Returns individual inventory records for each date and room type.
    """
    if end <= start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    query = select(Inventory).where(
        and_(
            Inventory.date >= start,
            Inventory.date < end
        )
    )
    
    if room_type_id:
        query = query.where(Inventory.room_type_id == room_type_id)
    
    query = query.order_by(Inventory.date, Inventory.room_type_id)
    
    result = await db.execute(query)
    inventories = result.scalars().all()
    
    # Get room type names for response
    room_types_result = await db.execute(select(RoomType))
    room_types = {rt.id: rt.name for rt in room_types_result.scalars().all()}
    
    return [
        InventoryRead(
            id=inv.id,
            room_type_id=inv.room_type_id,
            room_type_name=room_types.get(inv.room_type_id),
            date=inv.date,
            available_rooms=inv.available_rooms,
            price=inv.price
        )
        for inv in inventories
    ]


@router.put("/{inventory_id}", response_model=InventoryRead)
async def update_inventory(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific inventory record. (Protected - requires authentication)
    
    Allows adjusting available rooms or price for a specific date.
    """
    result = await db.execute(
        select(Inventory).where(Inventory.id == inventory_id)
    )
    inventory = result.scalar_one_or_none()
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record with ID {inventory_id} not found"
        )
    
    # Update fields if provided
    update_data = inventory_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inventory, field, value)
    
    await db.commit()
    await db.refresh(inventory)
    
    # Get room type name
    room_type_result = await db.execute(
        select(RoomType).where(RoomType.id == inventory.room_type_id)
    )
    room_type = room_type_result.scalar_one_or_none()
    
    return InventoryRead(
        id=inventory.id,
        room_type_id=inventory.room_type_id,
        room_type_name=room_type.name if room_type else None,
        date=inventory.date,
        available_rooms=inventory.available_rooms,
        price=inventory.price
    )


@router.post("/generate/{room_type_id}", status_code=status.HTTP_201_CREATED)
async def regenerate_inventory(
    room_type_id: int,
    days_ahead: int = Query(default=90, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Regenerate inventory for a room type. (Protected - requires authentication)
    
    Generates inventory for missing dates (does not overwrite existing).
    
    - **room_type_id**: ID of the room type
    - **days_ahead**: Number of days to generate (default: 90, max: 365)
    """
    result = await db.execute(
        select(RoomType).where(RoomType.id == room_type_id)
    )
    room_type = result.scalar_one_or_none()
    
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with ID {room_type_id} not found"
        )
    
    created_count = await generate_inventory_for_room_type(db, room_type, days_ahead)
    
    return {"message": f"Created {created_count} new inventory records"}

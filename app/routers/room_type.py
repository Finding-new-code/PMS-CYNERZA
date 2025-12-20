"""
Room type management router.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.room_type import RoomType
from app.schemas.room_type import RoomTypeCreate, RoomTypeRead, RoomTypeUpdate
from app.services.inventory_service import generate_inventory_for_room_type

router = APIRouter(prefix="/room-types", tags=["Room Types"])


@router.get("", response_model=List[RoomTypeRead])
async def list_room_types(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all room types.
    
    Returns a list of all available room types with their details.
    """
    result = await db.execute(select(RoomType).order_by(RoomType.name))
    room_types = result.scalars().all()
    return room_types


@router.get("/{room_type_id}", response_model=RoomTypeRead)
async def get_room_type(
    room_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific room type by ID.
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
    
    return room_type


@router.post("", response_model=RoomTypeRead, status_code=status.HTTP_201_CREATED)
async def create_room_type(
    room_type_data: RoomTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new room type. (Protected - requires authentication)
    
    Automatically generates inventory for the next 90 days.
    
    - **name**: Unique room type name (e.g., "Deluxe", "Suite")
    - **total_rooms**: Number of rooms of this type
    - **base_price**: Base price per night
    - **description**: Optional description
    """
    # Check if name already exists
    existing = await db.execute(
        select(RoomType).where(RoomType.name == room_type_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room type '{room_type_data.name}' already exists"
        )
    
    # Create room type
    room_type = RoomType(
        name=room_type_data.name,
        total_rooms=room_type_data.total_rooms,
        base_price=room_type_data.base_price,
        description=room_type_data.description
    )
    db.add(room_type)
    await db.commit()
    await db.refresh(room_type)
    
    # Generate inventory for next 90 days
    await generate_inventory_for_room_type(db, room_type)
    
    return room_type


@router.put("/{room_type_id}", response_model=RoomTypeRead)
async def update_room_type(
    room_type_id: int,
    room_type_data: RoomTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a room type. (Protected - requires authentication)
    
    Note: Changing total_rooms does not automatically update existing inventory.
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
    
    # Update fields if provided
    update_data = room_type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room_type, field, value)
    
    await db.commit()
    await db.refresh(room_type)
    
    return room_type


@router.delete("/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_type(
    room_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a room type. (Protected - requires authentication)
    
    This will also delete all associated inventory records.
    Will fail if there are existing bookings for this room type.
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
    
    # Check for existing bookings
    if room_type.bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete room type with existing bookings"
        )
    
    await db.delete(room_type)
    await db.commit()

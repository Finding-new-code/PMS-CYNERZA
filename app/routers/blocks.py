"""
Room Blocks API router.
Handles maintenance, holds, and out-of-service room management.
"""

from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.room_block import BlockType, BlockStatus
from app.schemas.block import RoomBlockCreate, RoomBlockResponse
from app.services import block_service

router = APIRouter(prefix="/blocks", tags=["Room Blocks"])


@router.get("/", response_model=List[RoomBlockResponse])
async def get_blocks(
    start_date: date,
    end_date: date,
    room_type_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all active room blocks within a date range.
    """
    blocks = await block_service.get_active_blocks(
        db, start_date, end_date, room_type_id
    )
    return blocks


@router.post("/", response_model=RoomBlockResponse, status_code=status.HTTP_201_CREATED)
async def create_block(
    block_data: RoomBlockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new room block.
    This will reduce available inventory for the specified date range.
    """
    if block_data.end_date < block_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    block = await block_service.create_block(
        db=db,
        room_type_id=block_data.room_type_id,
        start_date=block_data.start_date,
        end_date=block_data.end_date,
        block_type=BlockType(block_data.block_type.value),
        num_rooms=block_data.num_rooms,
        reason=block_data.reason,
        release_date=block_data.release_date,
        created_by=current_user.id,
    )
    return block


@router.post("/{block_id}/release", response_model=RoomBlockResponse)
async def release_block(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Release a room block, restoring inventory.
    """
    block = await block_service.release_block(db, block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found or already released"
        )
    return block


@router.post("/auto-release", response_model=dict)
async def trigger_auto_release(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger auto-release of expired holds.
    In production, this would be a scheduled background task.
    """
    count = await block_service.auto_release_expired_holds(db)
    return {"released_count": count}

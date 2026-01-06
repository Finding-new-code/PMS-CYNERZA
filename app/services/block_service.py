"""
Block service for managing room blocks (maintenance, holds, out-of-service).
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.room_block import RoomBlock, BlockType, BlockStatus
from app.models.inventory import Inventory


async def create_block(
    db: AsyncSession,
    room_type_id: int,
    start_date: date,
    end_date: date,
    block_type: BlockType,
    num_rooms: int,
    reason: Optional[str] = None,
    release_date: Optional[date] = None,
    created_by: Optional[int] = None,
) -> RoomBlock:
    """
    Create a new room block and update inventory accordingly.
    """
    block = RoomBlock(
        room_type_id=room_type_id,
        start_date=start_date,
        end_date=end_date,
        block_type=block_type,
        num_rooms=num_rooms,
        reason=reason,
        release_date=release_date,
        created_by=created_by,
        status=BlockStatus.ACTIVE,
    )
    db.add(block)
    
    # Update inventory for the date range
    await _adjust_inventory(db, room_type_id, start_date, end_date, -num_rooms)
    
    await db.commit()
    await db.refresh(block)
    return block


async def release_block(db: AsyncSession, block_id: int) -> Optional[RoomBlock]:
    """
    Release a block and restore inventory.
    """
    result = await db.execute(
        select(RoomBlock).where(RoomBlock.id == block_id)
    )
    block = result.scalar_one_or_none()
    
    if not block or block.status != BlockStatus.ACTIVE:
        return None
    
    block.status = BlockStatus.RELEASED
    
    # Restore inventory
    await _adjust_inventory(
        db, block.room_type_id, block.start_date, block.end_date, block.num_rooms
    )
    
    await db.commit()
    await db.refresh(block)
    return block


async def get_active_blocks(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    room_type_id: Optional[int] = None,
) -> List[RoomBlock]:
    """
    Get all active blocks overlapping the given date range.
    """
    query = select(RoomBlock).where(
        and_(
            RoomBlock.status == BlockStatus.ACTIVE,
            RoomBlock.start_date <= end_date,
            RoomBlock.end_date >= start_date,
        )
    )
    
    if room_type_id:
        query = query.where(RoomBlock.room_type_id == room_type_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def auto_release_expired_holds(db: AsyncSession) -> int:
    """
    Background task to release holds that have passed their release_date.
    Returns the number of blocks released.
    """
    today = date.today()
    
    result = await db.execute(
        select(RoomBlock).where(
            and_(
                RoomBlock.status == BlockStatus.ACTIVE,
                RoomBlock.block_type == BlockType.HOLD,
                RoomBlock.release_date != None,
                RoomBlock.release_date <= today,
            )
        )
    )
    expired_blocks = result.scalars().all()
    
    count = 0
    for block in expired_blocks:
        block.status = BlockStatus.EXPIRED
        await _adjust_inventory(
            db, block.room_type_id, block.start_date, block.end_date, block.num_rooms
        )
        count += 1
    
    if count > 0:
        await db.commit()
    
    return count


async def _adjust_inventory(
    db: AsyncSession,
    room_type_id: int,
    start_date: date,
    end_date: date,
    adjustment: int,
) -> None:
    """
    Adjust inventory available_rooms for a date range.
    Positive adjustment = add rooms, negative = remove rooms.
    """
    result = await db.execute(
        select(Inventory).where(
            and_(
                Inventory.room_type_id == room_type_id,
                Inventory.date >= start_date,
                Inventory.date <= end_date,
            )
        )
    )
    inventory_records = result.scalars().all()
    
    for inv in inventory_records:
        inv.available_rooms = inv.available_rooms + adjustment

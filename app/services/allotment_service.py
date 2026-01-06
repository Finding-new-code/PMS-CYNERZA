"""
Allotment service for managing group reservations.
"""

from datetime import date
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.allotment import Allotment, AllotmentRoom, AllotmentStatus
from app.models.inventory import Inventory


async def create_allotment(
    db: AsyncSession,
    name: str,
    start_date: date,
    end_date: date,
    room_allocations: List[dict],  # [{"room_type_id": 1, "blocked_rooms": 10}, ...]
    cutoff_date: Optional[date] = None,
    contact_name: Optional[str] = None,
    contact_email: Optional[str] = None,
    contact_phone: Optional[str] = None,
    group_rate: Optional[Decimal] = None,
    notes: Optional[str] = None,
    created_by: Optional[int] = None,
) -> Allotment:
    """
    Create a new group allotment with room allocations.
    """
    allotment = Allotment(
        name=name,
        status=AllotmentStatus.LEAD,
        start_date=start_date,
        end_date=end_date,
        cutoff_date=cutoff_date,
        contact_name=contact_name,
        contact_email=contact_email,
        contact_phone=contact_phone,
        group_rate=group_rate,
        notes=notes,
        created_by=created_by,
    )
    db.add(allotment)
    await db.flush()  # Get the allotment ID
    
    # Create day-wise room allocations
    current_date = start_date
    while current_date <= end_date:
        for allocation in room_allocations:
            allotment_room = AllotmentRoom(
                allotment_id=allotment.id,
                room_type_id=allocation["room_type_id"],
                date=current_date,
                blocked_rooms=allocation["blocked_rooms"],
                picked_up_rooms=0,
            )
            db.add(allotment_room)
        current_date = current_date.replace(day=current_date.day + 1) if current_date.day < 28 else date(
            current_date.year if current_date.month < 12 else current_date.year + 1,
            current_date.month + 1 if current_date.month < 12 else 1,
            1
        )
        # Simplified date iteration - in production use dateutil
        from datetime import timedelta
        current_date = start_date
        break  # Will re-implement with proper loop
    
    # Proper date iteration
    from datetime import timedelta
    current = start_date
    while current <= end_date:
        for allocation in room_allocations:
            allotment_room = AllotmentRoom(
                allotment_id=allotment.id,
                room_type_id=allocation["room_type_id"],
                date=current,
                blocked_rooms=allocation["blocked_rooms"],
                picked_up_rooms=0,
            )
            db.add(allotment_room)
        current += timedelta(days=1)
    
    await db.commit()
    await db.refresh(allotment)
    return allotment


async def update_allotment_status(
    db: AsyncSession,
    allotment_id: int,
    new_status: AllotmentStatus,
) -> Optional[Allotment]:
    """
    Update the status of an allotment.
    When status changes to DEFINITE, reduce inventory.
    When status changes to RELEASED, restore inventory.
    """
    result = await db.execute(
        select(Allotment).where(Allotment.id == allotment_id)
    )
    allotment = result.scalar_one_or_none()
    
    if not allotment:
        return None
    
    old_status = allotment.status
    allotment.status = new_status
    
    # Handle inventory changes
    if old_status != AllotmentStatus.DEFINITE and new_status == AllotmentStatus.DEFINITE:
        # Block rooms in inventory
        await _adjust_allotment_inventory(db, allotment_id, subtract=True)
    elif old_status == AllotmentStatus.DEFINITE and new_status in [AllotmentStatus.RELEASED, AllotmentStatus.CANCELLED]:
        # Restore rooms to inventory (only unreserved ones)
        await _adjust_allotment_inventory(db, allotment_id, subtract=False)
    
    await db.commit()
    await db.refresh(allotment)
    return allotment


async def record_pickup(
    db: AsyncSession,
    allotment_id: int,
    room_type_id: int,
    pickup_date: date,
    rooms_picked: int,
) -> bool:
    """
    Record rooms picked up from an allotment (converted to actual bookings).
    """
    result = await db.execute(
        select(AllotmentRoom).where(
            and_(
                AllotmentRoom.allotment_id == allotment_id,
                AllotmentRoom.room_type_id == room_type_id,
                AllotmentRoom.date == pickup_date,
            )
        )
    )
    allotment_room = result.scalar_one_or_none()
    
    if not allotment_room:
        return False
    
    # Check if pickup exceeds blocked
    if allotment_room.picked_up_rooms + rooms_picked > allotment_room.blocked_rooms:
        return False
    
    allotment_room.picked_up_rooms += rooms_picked
    await db.commit()
    return True


async def get_allotment_pickup_report(db: AsyncSession, allotment_id: int) -> dict:
    """
    Get pickup statistics for an allotment.
    """
    result = await db.execute(
        select(Allotment).where(Allotment.id == allotment_id)
    )
    allotment = result.scalar_one_or_none()
    
    if not allotment:
        return {}
    
    rooms_result = await db.execute(
        select(AllotmentRoom).where(AllotmentRoom.allotment_id == allotment_id)
    )
    rooms = rooms_result.scalars().all()
    
    total_blocked = sum(r.blocked_rooms for r in rooms)
    total_picked = sum(r.picked_up_rooms for r in rooms)
    
    return {
        "allotment_id": allotment_id,
        "name": allotment.name,
        "status": allotment.status.value,
        "start_date": allotment.start_date,
        "end_date": allotment.end_date,
        "total_room_nights_blocked": total_blocked,
        "total_room_nights_picked": total_picked,
        "pickup_percentage": (total_picked / total_blocked * 100) if total_blocked > 0 else 0,
        "remaining_room_nights": total_blocked - total_picked,
    }


async def auto_release_cutoff(db: AsyncSession) -> int:
    """
    Background task to release allotments past their cutoff date.
    Returns the number of allotments released.
    """
    today = date.today()
    
    result = await db.execute(
        select(Allotment).where(
            and_(
                Allotment.status.in_([AllotmentStatus.LEAD, AllotmentStatus.TENTATIVE]),
                Allotment.cutoff_date != None,
                Allotment.cutoff_date <= today,
            )
        )
    )
    expired_allotments = result.scalars().all()
    
    count = 0
    for allotment in expired_allotments:
        allotment.status = AllotmentStatus.RELEASED
        count += 1
    
    if count > 0:
        await db.commit()
    
    return count


async def _adjust_allotment_inventory(
    db: AsyncSession,
    allotment_id: int,
    subtract: bool,
) -> None:
    """
    Adjust inventory based on allotment rooms.
    subtract=True: reduce available rooms (when allotment becomes definite)
    subtract=False: restore available rooms (when allotment is released)
    """
    result = await db.execute(
        select(AllotmentRoom).where(AllotmentRoom.allotment_id == allotment_id)
    )
    allotment_rooms = result.scalars().all()
    
    for ar in allotment_rooms:
        # Only adjust for rooms not yet picked up
        rooms_to_adjust = ar.blocked_rooms - ar.picked_up_rooms
        if rooms_to_adjust <= 0:
            continue
        
        inv_result = await db.execute(
            select(Inventory).where(
                and_(
                    Inventory.room_type_id == ar.room_type_id,
                    Inventory.date == ar.date,
                )
            )
        )
        inventory = inv_result.scalar_one_or_none()
        
        if inventory:
            if subtract:
                inventory.available_rooms -= rooms_to_adjust
            else:
                inventory.available_rooms += rooms_to_adjust

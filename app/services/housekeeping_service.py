"""
Housekeeping service for managing room status and housekeeping tasks.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.room import Room, RoomStatus, OccupancyStatus
from app.models.housekeeping_task import HousekeepingTask, TaskType, TaskStatus, TaskPriority
from app.models.user import User
from app.models.booking import Booking


async def get_rooms(
    db: AsyncSession,
    status_filter: Optional[RoomStatus] = None,
    occupancy_filter: Optional[OccupancyStatus] = None,
    floor: Optional[int] = None,
    assigned_to: Optional[int] = None
) -> List[Room]:
    """Get all rooms with optional filters."""
    query = select(Room).options(
        selectinload(Room.room_type),
        selectinload(Room.assigned_housekeeper)
    ).where(Room.is_active == True)
    
    if status_filter:
        query = query.where(Room.housekeeping_status == status_filter)
    if occupancy_filter:
        query = query.where(Room.occupancy_status == occupancy_filter)
    if floor:
        query = query.where(Room.floor == floor)
    if assigned_to:
        query = query.where(Room.assigned_housekeeper_id == assigned_to)
    
    query = query.order_by(Room.floor, Room.room_number)
    result = await db.execute(query)
    return result.scalars().all()


async def get_room_by_id(db: AsyncSession, room_id: int) -> Optional[Room]:
    """Get a specific room by ID."""
    query = select(Room).options(
        selectinload(Room.room_type),
        selectinload(Room.assigned_housekeeper)
    ).where(Room.id == room_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_room_by_number(db: AsyncSession, room_number: str) -> Optional[Room]:
    """Get a room by its room number."""
    query = select(Room).where(Room.room_number == room_number)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_room(db: AsyncSession, room_data: dict) -> Room:
    """Create a new room."""
    room = Room(**room_data)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def update_room_status(
    db: AsyncSession,
    room_id: int,
    new_status: RoomStatus,
    notes: Optional[str] = None
) -> Optional[Room]:
    """Update a room's housekeeping status."""
    room = await get_room_by_id(db, room_id)
    if not room:
        return None
    
    room.housekeeping_status = new_status
    room.status_updated_at = datetime.utcnow()
    
    if new_status == RoomStatus.CLEAN:
        room.last_cleaned_at = datetime.utcnow()
    elif new_status == RoomStatus.INSPECTED:
        room.last_inspected_at = datetime.utcnow()
    
    if notes:
        room.housekeeping_notes = notes
    
    await db.commit()
    await db.refresh(room)
    return room


async def assign_housekeeper(
    db: AsyncSession,
    room_id: int,
    housekeeper_id: int
) -> Optional[Room]:
    """Assign a housekeeper to a room."""
    room = await get_room_by_id(db, room_id)
    if not room:
        return None
    
    room.assigned_housekeeper_id = housekeeper_id
    await db.commit()
    await db.refresh(room)
    return room


async def bulk_update_status(
    db: AsyncSession,
    room_ids: List[int],
    new_status: RoomStatus
) -> int:
    """Update status for multiple rooms at once. Returns count of updated rooms."""
    updated = 0
    for room_id in room_ids:
        result = await update_room_status(db, room_id, new_status)
        if result:
            updated += 1
    return updated


async def reset_dirty_after_checkout(db: AsyncSession) -> int:
    """Mark all checkout rooms as dirty. Called after checkout processing."""
    query = select(Room).where(
        and_(
            Room.occupancy_status == OccupancyStatus.CHECKOUT,
            Room.housekeeping_status != RoomStatus.DIRTY
        )
    )
    result = await db.execute(query)
    rooms = result.scalars().all()
    
    for room in rooms:
        room.housekeeping_status = RoomStatus.DIRTY
        room.occupancy_status = OccupancyStatus.VACANT
        room.status_updated_at = datetime.utcnow()
    
    await db.commit()
    return len(rooms)


async def daily_housekeeping_reset(db: AsyncSession) -> dict:
    """
    Daily reset typically run at 2 AM:
    - Mark all occupied rooms as stayover
    - Set clean rooms back to dirty for stayover cleaning
    Returns stats about what was reset.
    """
    stats = {"stayover_rooms": 0, "rooms_set_dirty": 0}
    
    # Get occupied rooms
    query = select(Room).where(Room.occupancy_status == OccupancyStatus.OCCUPIED)
    result = await db.execute(query)
    occupied_rooms = result.scalars().all()
    
    for room in occupied_rooms:
        room.occupancy_status = OccupancyStatus.STAYOVER
        stats["stayover_rooms"] += 1
        
        # Optional: Set clean rooms to dirty for stayover cleaning
        if room.housekeeping_status == RoomStatus.CLEAN:
            room.housekeeping_status = RoomStatus.DIRTY
            stats["rooms_set_dirty"] += 1
    
    await db.commit()
    return stats


# Housekeeping Task Functions
async def create_task(
    db: AsyncSession,
    task_data: dict,
    assigned_by_id: int
) -> HousekeepingTask:
    """Create a new housekeeping task."""
    task = HousekeepingTask(
        **task_data,
        assigned_by_id=assigned_by_id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks(
    db: AsyncSession,
    status_filter: Optional[TaskStatus] = None,
    assigned_to: Optional[int] = None,
    task_date: Optional[date] = None
) -> List[HousekeepingTask]:
    """Get housekeeping tasks with filters."""
    query = select(HousekeepingTask).options(
        selectinload(HousekeepingTask.room),
        selectinload(HousekeepingTask.assigned_to)
    )
    
    if status_filter:
        query = query.where(HousekeepingTask.task_status == status_filter)
    if assigned_to:
        query = query.where(HousekeepingTask.assigned_to_id == assigned_to)
    if task_date:
        start = datetime.combine(task_date, datetime.min.time())
        end = datetime.combine(task_date, datetime.max.time())
        query = query.where(
            and_(
                HousekeepingTask.scheduled_date >= start,
                HousekeepingTask.scheduled_date <= end
            )
        )
    
    query = query.order_by(
        HousekeepingTask.priority.desc(),
        HousekeepingTask.scheduled_date
    )
    result = await db.execute(query)
    return result.scalars().all()


async def complete_task(
    db: AsyncSession,
    task_id: int,
    completion_notes: Optional[str] = None
) -> Optional[HousekeepingTask]:
    """Mark a task as completed."""
    query = select(HousekeepingTask).where(HousekeepingTask.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        return None
    
    task.task_status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    task.completion_notes = completion_notes
    
    # Update room status based on task type
    room = await get_room_by_id(db, task.room_id)
    if room:
        if task.task_type in [TaskType.CHECKOUT_CLEAN, TaskType.STAYOVER_CLEAN, TaskType.DEEP_CLEAN]:
            room.housekeeping_status = RoomStatus.CLEAN
            room.last_cleaned_at = datetime.utcnow()
        elif task.task_type == TaskType.INSPECTION:
            room.housekeeping_status = RoomStatus.INSPECTED
            room.last_inspected_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    return task


async def inspect_task(
    db: AsyncSession,
    task_id: int,
    inspector_id: int,
    passed: bool,
    notes: Optional[str] = None
) -> Optional[HousekeepingTask]:
    """Record inspection result for a cleaning task."""
    query = select(HousekeepingTask).where(HousekeepingTask.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        return None
    
    task.inspected_by_id = inspector_id
    task.inspection_passed = passed
    task.inspection_notes = notes
    
    # Update room to inspected if passed
    if passed:
        room = await get_room_by_id(db, task.room_id)
        if room:
            room.housekeeping_status = RoomStatus.INSPECTED
            room.last_inspected_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    return task


async def get_housekeeping_summary(db: AsyncSession) -> dict:
    """Get a summary of current housekeeping status."""
    # Room status counts
    status_query = select(
        Room.housekeeping_status,
        func.count(Room.id).label("count")
    ).where(Room.is_active == True).group_by(Room.housekeeping_status)
    
    result = await db.execute(status_query)
    status_counts = {row.housekeeping_status.value: row.count for row in result}
    
    # Task counts
    today = date.today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    
    pending_query = select(func.count(HousekeepingTask.id)).where(
        HousekeepingTask.task_status == TaskStatus.PENDING
    )
    pending = await db.execute(pending_query)
    
    in_progress_query = select(func.count(HousekeepingTask.id)).where(
        HousekeepingTask.task_status == TaskStatus.IN_PROGRESS
    )
    in_progress = await db.execute(in_progress_query)
    
    completed_today_query = select(func.count(HousekeepingTask.id)).where(
        and_(
            HousekeepingTask.task_status == TaskStatus.COMPLETED,
            HousekeepingTask.completed_at >= start,
            HousekeepingTask.completed_at <= end
        )
    )
    completed_today = await db.execute(completed_today_query)
    
    # Total rooms
    total_query = select(func.count(Room.id)).where(Room.is_active == True)
    total = await db.execute(total_query)
    
    return {
        "total_rooms": total.scalar() or 0,
        "dirty": status_counts.get("dirty", 0),
        "clean": status_counts.get("clean", 0),
        "inspected": status_counts.get("inspected", 0),
        "out_of_order": status_counts.get("out_of_order", 0),
        "out_of_service": status_counts.get("out_of_service", 0),
        "pending_tasks": pending.scalar() or 0,
        "in_progress_tasks": in_progress.scalar() or 0,
        "completed_today": completed_today.scalar() or 0
    }

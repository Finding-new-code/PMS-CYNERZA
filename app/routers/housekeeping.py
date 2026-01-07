"""
Router for housekeeping operations including room status and task management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.housekeeping import (
    RoomCreate, RoomUpdate, RoomRead, RoomStatusUpdate,
    HousekeepingTaskCreate, HousekeepingTaskUpdate, HousekeepingTaskRead,
    HousekeepingTaskComplete, HousekeepingTaskInspect,
    HousekeepingSummary, RoomStatusEnum, OccupancyStatusEnum, TaskStatusEnum
)
from app.services import housekeeping_service
from app.models.room import RoomStatus, OccupancyStatus
from app.models.housekeeping_task import TaskStatus

router = APIRouter(prefix="/housekeeping", tags=["Housekeeping"])


# ============ Room Endpoints ============

@router.get("/rooms", response_model=List[RoomRead])
async def list_rooms(
    status: Optional[RoomStatusEnum] = Query(None, description="Filter by housekeeping status"),
    occupancy: Optional[OccupancyStatusEnum] = Query(None, description="Filter by occupancy status"),
    floor: Optional[int] = Query(None, description="Filter by floor number"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned housekeeper ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all rooms with optional filters."""
    status_filter = RoomStatus(status.value) if status else None
    occupancy_filter = OccupancyStatus(occupancy.value) if occupancy else None
    
    rooms = await housekeeping_service.get_rooms(
        db, status_filter, occupancy_filter, floor, assigned_to
    )
    
    return [
        RoomRead(
            id=r.id,
            room_number=r.room_number,
            room_type_id=r.room_type_id,
            room_type_name=r.room_type.name if r.room_type else None,
            floor=r.floor,
            housekeeping_status=RoomStatusEnum(r.housekeeping_status.value),
            occupancy_status=OccupancyStatusEnum(r.occupancy_status.value),
            assigned_housekeeper_id=r.assigned_housekeeper_id,
            assigned_housekeeper_name=r.assigned_housekeeper.email if r.assigned_housekeeper else None,
            priority=r.priority,
            housekeeping_notes=r.housekeeping_notes,
            last_cleaned_at=r.last_cleaned_at,
            last_inspected_at=r.last_inspected_at,
            status_updated_at=r.status_updated_at,
            is_active=r.is_active
        )
        for r in rooms
    ]


@router.get("/rooms/{room_id}", response_model=RoomRead)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific room by ID."""
    room = await housekeeping_service.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return RoomRead(
        id=room.id,
        room_number=room.room_number,
        room_type_id=room.room_type_id,
        room_type_name=room.room_type.name if room.room_type else None,
        floor=room.floor,
        housekeeping_status=RoomStatusEnum(room.housekeeping_status.value),
        occupancy_status=OccupancyStatusEnum(room.occupancy_status.value),
        assigned_housekeeper_id=room.assigned_housekeeper_id,
        assigned_housekeeper_name=room.assigned_housekeeper.email if room.assigned_housekeeper else None,
        priority=room.priority,
        housekeeping_notes=room.housekeeping_notes,
        last_cleaned_at=room.last_cleaned_at,
        last_inspected_at=room.last_inspected_at,
        status_updated_at=room.status_updated_at,
        is_active=room.is_active
    )


@router.post("/rooms", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new room."""
    # Check if room number already exists
    existing = await housekeeping_service.get_room_by_number(db, room_data.room_number)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Room {room_data.room_number} already exists"
        )
    
    room = await housekeeping_service.create_room(db, room_data.model_dump())
    
    # Reload with relationships
    room = await housekeeping_service.get_room_by_id(db, room.id)
    
    return RoomRead(
        id=room.id,
        room_number=room.room_number,
        room_type_id=room.room_type_id,
        room_type_name=room.room_type.name if room.room_type else None,
        floor=room.floor,
        housekeeping_status=RoomStatusEnum(room.housekeeping_status.value),
        occupancy_status=OccupancyStatusEnum(room.occupancy_status.value),
        assigned_housekeeper_id=room.assigned_housekeeper_id,
        assigned_housekeeper_name=None,
        priority=room.priority,
        housekeeping_notes=room.housekeeping_notes,
        last_cleaned_at=room.last_cleaned_at,
        last_inspected_at=room.last_inspected_at,
        status_updated_at=room.status_updated_at,
        is_active=room.is_active
    )


@router.patch("/rooms/{room_id}/status", response_model=RoomRead)
async def update_room_status(
    room_id: int,
    status_update: RoomStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update room housekeeping status (Dirty/Clean/Inspected)."""
    room = await housekeeping_service.update_room_status(
        db, room_id, 
        RoomStatus(status_update.housekeeping_status.value),
        status_update.notes
    )
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return RoomRead(
        id=room.id,
        room_number=room.room_number,
        room_type_id=room.room_type_id,
        room_type_name=room.room_type.name if room.room_type else None,
        floor=room.floor,
        housekeeping_status=RoomStatusEnum(room.housekeeping_status.value),
        occupancy_status=OccupancyStatusEnum(room.occupancy_status.value),
        assigned_housekeeper_id=room.assigned_housekeeper_id,
        assigned_housekeeper_name=room.assigned_housekeeper.email if room.assigned_housekeeper else None,
        priority=room.priority,
        housekeeping_notes=room.housekeeping_notes,
        last_cleaned_at=room.last_cleaned_at,
        last_inspected_at=room.last_inspected_at,
        status_updated_at=room.status_updated_at,
        is_active=room.is_active
    )


@router.post("/rooms/{room_id}/assign")
async def assign_housekeeper(
    room_id: int,
    housekeeper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a housekeeper to a room."""
    room = await housekeeping_service.assign_housekeeper(db, room_id, housekeeper_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": f"Housekeeper {housekeeper_id} assigned to room {room.room_number}"}


@router.post("/rooms/bulk-status-update")
async def bulk_update_room_status(
    room_ids: List[int],
    status: RoomStatusEnum,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update status for multiple rooms at once."""
    count = await housekeeping_service.bulk_update_status(
        db, room_ids, RoomStatus(status.value)
    )
    return {"message": f"Updated {count} rooms to {status.value}"}


# ============ Task Endpoints ============

@router.get("/tasks", response_model=List[HousekeepingTaskRead])
async def list_tasks(
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by task status"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned housekeeper"),
    task_date: Optional[date] = Query(None, description="Filter by scheduled date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get housekeeping tasks with optional filters."""
    status_filter = TaskStatus(status.value) if status else None
    
    tasks = await housekeeping_service.get_tasks(db, status_filter, assigned_to, task_date)
    
    return [
        HousekeepingTaskRead(
            id=t.id,
            room_id=t.room_id,
            room_number=t.room.room_number if t.room else None,
            task_type=t.task_type.value,
            task_status=t.task_status.value,
            priority=t.priority.value,
            assigned_to_id=t.assigned_to_id,
            assigned_to_name=t.assigned_to.email if t.assigned_to else None,
            assigned_by_id=t.assigned_by_id,
            scheduled_date=t.scheduled_date,
            started_at=t.started_at,
            completed_at=t.completed_at,
            notes=t.notes,
            completion_notes=t.completion_notes,
            inspected_by_id=t.inspected_by_id,
            inspection_passed=t.inspection_passed,
            inspection_notes=t.inspection_notes,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in tasks
    ]


@router.post("/tasks", response_model=HousekeepingTaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: HousekeepingTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new housekeeping task."""
    task = await housekeeping_service.create_task(
        db, task_data.model_dump(), current_user.id
    )
    
    return HousekeepingTaskRead(
        id=task.id,
        room_id=task.room_id,
        room_number=None,
        task_type=task.task_type.value,
        task_status=task.task_status.value,
        priority=task.priority.value,
        assigned_to_id=task.assigned_to_id,
        assigned_to_name=None,
        assigned_by_id=task.assigned_by_id,
        scheduled_date=task.scheduled_date,
        started_at=task.started_at,
        completed_at=task.completed_at,
        notes=task.notes,
        completion_notes=task.completion_notes,
        inspected_by_id=task.inspected_by_id,
        inspection_passed=task.inspection_passed,
        inspection_notes=task.inspection_notes,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    completion: HousekeepingTaskComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a task as completed."""
    task = await housekeeping_service.complete_task(db, task_id, completion.completion_notes)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": f"Task {task_id} completed", "room_status": task.room.housekeeping_status.value if task.room else None}


@router.post("/tasks/{task_id}/inspect")
async def inspect_task(
    task_id: int,
    inspection: HousekeepingTaskInspect,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record inspection result for a task."""
    task = await housekeeping_service.inspect_task(
        db, task_id, current_user.id,
        inspection.inspection_passed, inspection.inspection_notes
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "message": f"Inspection {'passed' if inspection.inspection_passed else 'failed'}",
        "task_id": task_id
    }


# ============ Reports & Triggers ============

@router.get("/summary", response_model=HousekeepingSummary)
async def get_housekeeping_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get housekeeping status summary."""
    summary = await housekeeping_service.get_housekeeping_summary(db)
    return HousekeepingSummary(**summary)


@router.post("/triggers/checkout-reset")
async def trigger_checkout_reset(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger checkout room reset (mark checkout rooms as dirty)."""
    count = await housekeeping_service.reset_dirty_after_checkout(db)
    return {"message": f"Marked {count} checkout rooms as dirty"}


@router.post("/triggers/daily-reset")
async def trigger_daily_reset(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger daily housekeeping reset (2 AM reset simulation)."""
    stats = await housekeeping_service.daily_housekeeping_reset(db)
    return {
        "message": "Daily reset completed",
        "stayover_rooms": stats["stayover_rooms"],
        "rooms_set_dirty": stats["rooms_set_dirty"]
    }

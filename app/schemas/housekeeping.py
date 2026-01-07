"""
Pydantic schemas for Room and Housekeeping.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class RoomStatusEnum(str, Enum):
    DIRTY = "dirty"
    CLEAN = "clean"
    INSPECTED = "inspected"
    OUT_OF_ORDER = "out_of_order"
    OUT_OF_SERVICE = "out_of_service"


class OccupancyStatusEnum(str, Enum):
    VACANT = "vacant"
    OCCUPIED = "occupied"
    CHECKOUT = "checkout"
    CHECKIN = "checkin"
    STAYOVER = "stayover"


class TaskTypeEnum(str, Enum):
    CHECKOUT_CLEAN = "checkout_clean"
    STAYOVER_CLEAN = "stayover_clean"
    INSPECTION = "inspection"
    TURNDOWN = "turndown"
    DEEP_CLEAN = "deep_clean"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Room Schemas
class RoomBase(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=20)
    room_type_id: int
    floor: Optional[int] = None
    priority: Optional[int] = 0
    housekeeping_notes: Optional[str] = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_type_id: Optional[int] = None
    floor: Optional[int] = None
    housekeeping_status: Optional[RoomStatusEnum] = None
    occupancy_status: Optional[OccupancyStatusEnum] = None
    assigned_housekeeper_id: Optional[int] = None
    priority: Optional[int] = None
    housekeeping_notes: Optional[str] = None
    is_active: Optional[bool] = None


class RoomStatusUpdate(BaseModel):
    """Quick status update for housekeeping."""
    housekeeping_status: RoomStatusEnum
    notes: Optional[str] = None


class RoomRead(BaseModel):
    id: int
    room_number: str
    room_type_id: int
    room_type_name: Optional[str] = None
    floor: Optional[int] = None
    housekeeping_status: RoomStatusEnum
    occupancy_status: OccupancyStatusEnum
    assigned_housekeeper_id: Optional[int] = None
    assigned_housekeeper_name: Optional[str] = None
    priority: int
    housekeeping_notes: Optional[str] = None
    last_cleaned_at: Optional[datetime] = None
    last_inspected_at: Optional[datetime] = None
    status_updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


# Housekeeping Task Schemas
class HousekeepingTaskCreate(BaseModel):
    room_id: int
    task_type: TaskTypeEnum
    priority: Optional[TaskPriorityEnum] = TaskPriorityEnum.NORMAL
    assigned_to_id: Optional[int] = None
    scheduled_date: datetime
    notes: Optional[str] = None


class HousekeepingTaskUpdate(BaseModel):
    task_status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    assigned_to_id: Optional[int] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None


class HousekeepingTaskComplete(BaseModel):
    completion_notes: Optional[str] = None


class HousekeepingTaskInspect(BaseModel):
    inspection_passed: bool
    inspection_notes: Optional[str] = None


class HousekeepingTaskRead(BaseModel):
    id: int
    room_id: int
    room_number: Optional[str] = None
    task_type: TaskTypeEnum
    task_status: TaskStatusEnum
    priority: TaskPriorityEnum
    assigned_to_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    assigned_by_id: Optional[int] = None
    scheduled_date: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    inspected_by_id: Optional[int] = None
    inspection_passed: Optional[bool] = None
    inspection_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Housekeeping Summary/Report Schemas
class HousekeepingSummary(BaseModel):
    total_rooms: int
    dirty: int
    clean: int
    inspected: int
    out_of_order: int
    out_of_service: int
    pending_tasks: int
    in_progress_tasks: int
    completed_today: int


class HousekeeperWorkload(BaseModel):
    housekeeper_id: int
    housekeeper_name: str
    assigned_rooms: int
    pending_tasks: int
    completed_today: int

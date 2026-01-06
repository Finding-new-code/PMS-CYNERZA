"""
Pydantic schemas for room blocks.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class BlockTypeEnum(str, Enum):
    MAINTENANCE = "maintenance"
    HOLD = "hold"
    OUT_OF_SERVICE = "out_of_service"


class BlockStatusEnum(str, Enum):
    ACTIVE = "active"
    RELEASED = "released"
    EXPIRED = "expired"
    CONVERTED = "converted"


class RoomBlockCreate(BaseModel):
    """Schema for creating a room block."""
    room_type_id: int = Field(..., gt=0)
    start_date: date
    end_date: date
    block_type: BlockTypeEnum
    num_rooms: int = Field(..., ge=1)
    reason: Optional[str] = Field(None, max_length=500)
    release_date: Optional[date] = None

    class Config:
        from_attributes = True


class RoomBlockResponse(BaseModel):
    """Schema for room block response."""
    id: int
    room_type_id: int
    start_date: date
    end_date: date
    block_type: BlockTypeEnum
    num_rooms: int
    reason: Optional[str]
    status: BlockStatusEnum
    release_date: Optional[date]

    class Config:
        from_attributes = True

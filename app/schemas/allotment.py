"""
Pydantic schemas for allotments.
"""

from datetime import date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class AllotmentStatusEnum(str, Enum):
    LEAD = "lead"
    TENTATIVE = "tentative"
    DEFINITE = "definite"
    RELEASED = "released"
    CANCELLED = "cancelled"


class RoomAllocation(BaseModel):
    """Room allocation for an allotment."""
    room_type_id: int = Field(..., gt=0)
    blocked_rooms: int = Field(..., ge=1)


class AllotmentCreate(BaseModel):
    """Schema for creating an allotment."""
    name: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: date
    cutoff_date: Optional[date] = None
    room_allocations: List[RoomAllocation]
    contact_name: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    group_rate: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AllotmentStatusUpdate(BaseModel):
    """Schema for updating allotment status."""
    status: AllotmentStatusEnum


class AllotmentResponse(BaseModel):
    """Schema for allotment response."""
    id: int
    name: str
    status: AllotmentStatusEnum
    start_date: date
    end_date: date
    cutoff_date: Optional[date]
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    group_rate: Optional[Decimal]
    notes: Optional[str]

    class Config:
        from_attributes = True


class AllotmentPickupReport(BaseModel):
    """Schema for allotment pickup report."""
    allotment_id: int
    name: str
    status: str
    start_date: date
    end_date: date
    total_room_nights_blocked: int
    total_room_nights_picked: int
    pickup_percentage: float
    remaining_room_nights: int

    class Config:
        from_attributes = True

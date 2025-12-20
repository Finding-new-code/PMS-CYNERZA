"""
Pydantic schemas for room type management.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class RoomTypeBase(BaseModel):
    """Base room type schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Room type name")
    total_rooms: int = Field(..., gt=0, description="Total number of rooms of this type")
    base_price: Decimal = Field(..., gt=0, description="Base price per night")
    description: Optional[str] = Field(None, max_length=500, description="Room type description")


class RoomTypeCreate(RoomTypeBase):
    """Schema for creating a new room type."""
    pass


class RoomTypeUpdate(BaseModel):
    """Schema for updating a room type."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    total_rooms: Optional[int] = Field(None, gt=0)
    base_price: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)


class RoomTypeRead(RoomTypeBase):
    """Schema for reading room type data."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

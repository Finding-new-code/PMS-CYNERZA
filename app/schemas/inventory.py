"""
Pydantic schemas for inventory management.
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from decimal import Decimal


class InventoryBase(BaseModel):
    """Base inventory schema."""
    room_type_id: int
    date: date
    available_rooms: int = Field(..., ge=0)
    price: Decimal = Field(..., gt=0)


class InventoryRead(InventoryBase):
    """Schema for reading inventory data."""
    id: int
    room_type_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class InventoryQuery(BaseModel):
    """Schema for querying inventory by date range."""
    start_date: date
    end_date: date
    room_type_id: Optional[int] = None


class InventoryUpdate(BaseModel):
    """Schema for updating inventory."""
    available_rooms: Optional[int] = Field(None, ge=0)
    price: Optional[Decimal] = Field(None, gt=0)


class InventoryAvailability(BaseModel):
    """Schema for availability check response."""
    room_type_id: int
    room_type_name: str
    date: date
    available_rooms: int
    price: Decimal


class DateRangeAvailability(BaseModel):
    """Availability summary for a date range."""
    room_type_id: int
    room_type_name: str
    start_date: date
    end_date: date
    min_available: int
    total_price: Decimal
    daily_breakdown: List[InventoryAvailability]

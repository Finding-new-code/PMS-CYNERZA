"""
Pydantic schemas for calendar API responses.
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Literal
from decimal import Decimal


class CalendarAvailability(BaseModel):
    """
    Single cell in the availability grid.
    Represents one room type on one date.
    """
    date: date
    room_type_id: int
    room_type_name: str
    available_rooms: int = Field(..., ge=0)
    total_rooms: int = Field(..., ge=0)
    price: Decimal
    status: Literal["available", "partial", "full"]
    
    class Config:
        from_attributes = True


class BookingEvent(BaseModel):
    """
    Calendar event block representing a booking.
    Used to display booking bars on the calendar.
    """
    booking_id: int
    title: str
    room_type_id: int
    room_type_name: str
    customer_name: str
    start: date  # check_in
    end: date    # check_out
    num_rooms: int
    status: str
    
    class Config:
        from_attributes = True


class CalendarSummary(BaseModel):
    """
    Summary statistics for a date range.
    """
    start_date: date
    end_date: date
    total_bookings: int
    total_rooms_booked: int
    occupancy_percentage: float

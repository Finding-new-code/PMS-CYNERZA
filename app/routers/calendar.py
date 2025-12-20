"""
Calendar API router for frontend calendar views.
All business logic is delegated to calendar_service.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.exceptions import InvalidDateRangeError, PMSException
from app.models.user import User
from app.schemas.calendar import CalendarAvailability, BookingEvent, CalendarSummary
from app.services.calendar_service import (
    get_availability_grid,
    get_booking_events,
    get_calendar_summary
)

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/availability", response_model=List[CalendarAvailability])
async def get_availability(
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    room_type_id: Optional[int] = Query(None, description="Filter by room type ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get availability grid for calendar view. (Protected - requires authentication)
    
    Returns availability status for each room type on each date.
    
    **Status values:**
    - `available`: All rooms available (available_rooms == total_rooms)
    - `partial`: Some rooms booked (available_rooms > 0)
    - `full`: No rooms available (available_rooms == 0)
    
    **Response format:**
    ```json
    [
      {
        "date": "2025-01-20",
        "room_type_id": 1,
        "room_type_name": "Deluxe",
        "available_rooms": 3,
        "total_rooms": 5,
        "price": "150.00",
        "status": "partial"
      }
    ]
    ```
    """
    try:
        return await get_availability_grid(db, start, end, room_type_id)
    except PMSException as e:
        raise e.to_http_exception()


@router.get("/bookings", response_model=List[BookingEvent])
async def get_bookings(
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    room_type_id: Optional[int] = Query(None, description="Filter by room type ID"),
    include_cancelled: bool = Query(False, description="Include cancelled bookings"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bookings as calendar events. (Protected - requires authentication)
    
    Returns booking blocks that can be rendered on a calendar.
    Includes all bookings that overlap with the date range.
    
    **Response format:**
    ```json
    [
      {
        "booking_id": 1,
        "title": "Deluxe - John Doe",
        "room_type_id": 1,
        "room_type_name": "Deluxe",
        "customer_name": "John Doe",
        "start": "2025-01-20",
        "end": "2025-01-22",
        "num_rooms": 1,
        "status": "confirmed"
      }
    ]
    ```
    """
    try:
        return await get_booking_events(db, start, end, room_type_id, include_cancelled)
    except PMSException as e:
        raise e.to_http_exception()


@router.get("/summary", response_model=CalendarSummary)
async def get_summary(
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get calendar summary statistics. (Protected - requires authentication)
    
    Returns aggregated statistics for the date range including:
    - Total bookings
    - Total rooms booked
    - Overall occupancy percentage
    """
    try:
        return await get_calendar_summary(db, start, end)
    except PMSException as e:
        raise e.to_http_exception()

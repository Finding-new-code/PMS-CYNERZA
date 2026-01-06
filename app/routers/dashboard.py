"""
Dashboard router - JWT-protected endpoints for real-time operational views.
Provides Today's Activity, 14-Day Forecast, and Quick Stats.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    TodaysActivity,
    ForecastAnalytics,
    QuickStats
)
from app.services.dashboard_service import (
    get_todays_activity,
    get_14day_forecast,
    get_quick_stats
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/todays-activity", response_model=TodaysActivity)
async def get_activity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time operational metrics for today.
    
    **Metrics:**
    - Arrivals: Expected, Checked-in, Pending
    - Departures: Expected, Checked-out, Pending  
    - In-House guests count
    - Issues: Overbookings, Cancellations, No-shows
    
    **Example Response:**
    ```json
    {
      "arrivals_expected": 12,
      "arrivals_checked_in": 5,
      "arrivals_pending": 7,
      "departures_expected": 8,
      "departures_checked_out": 3,
      "departures_pending": 5,
      "in_house_guests": 45,
      "overbookings": 0,
      "cancellations_today": 2,
      "no_shows": 0
    }
    ```
    """
    data = await get_todays_activity(db)
    return data


@router.get("/forecast", response_model=ForecastAnalytics)
async def get_forecast(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get 14-day forward-looking forecast.
    
    **Returns:**
    - Daily occupancy percentage
    - Available and booked rooms
    - Projected revenue
    - Arrivals and departures count
    - Peak and lowest occupancy days
    
    **Example Response:**
    ```json
    {
      "forecast_days": [
        {
          "date": "2025-01-07",
          "occupancy_percent": 75.5,
          "available_rooms": 10,
          "booked_rooms": 30,
          "projected_revenue": 15000.00,
          "arrivals": 8,
          "departures": 5
        }
      ],
      "avg_occupancy": 72.3,
      "total_projected_revenue": 210000.00,
      "peak_day": "2025-01-15",
      "lowest_day": "2025-01-09"
    }
    ```
    """
    data = await get_14day_forecast(db)
    return data


@router.get("/quick-stats", response_model=QuickStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get quick financial metrics for dashboard header.
    
    **Returns:**
    - Revenue: Today, MTD (Month to Date), YTD (Year to Date)
    - ADR (Average Daily Rate)
    - RevPAR (Revenue Per Available Room)
    - Today's occupancy percentage
    
    **Example Response:**
    ```json
    {
      "revenue_today": 25000.00,
      "revenue_mtd": 450000.00,
      "revenue_ytd": 2500000.00,
      "avg_daily_rate": 3125.00,
      "revpar": 2500.00,
      "occupancy_today": 80.0
    }
    ```
    """
    data = await get_quick_stats(db)
    return data

"""
Dashboard-specific schemas for enhanced operational views.
Provides real-time operational data and forecasting.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal


class TodaysActivity(BaseModel):
    """
    Real-time metrics for today's hotel operations.
    Displayed as the primary operational widget.
    """
    # Arrivals
    arrivals_expected: int  # Total expected today
    arrivals_checked_in: int  # Already checked in
    arrivals_pending: int  # Yet to arrive
    
    # Departures
    departures_expected: int  # Total expected today
    departures_checked_out: int  # Already checked out
    departures_pending: int  # Yet to depart
    
    # In-House
    in_house_guests: int  # Current occupancy
    
    # Issues
    overbookings: int  # Rooms overbooked for today
    cancellations_today: int  # Cancelled today
    no_shows: int  # Expected but didn't arrive (past check-in time)


class ForecastDay(BaseModel):
    """Forecast data for a single day."""
    date: date
    occupancy_percent: float
    available_rooms: int
    booked_rooms: int
    projected_revenue: Decimal
    arrivals: int
    departures: int


class ForecastAnalytics(BaseModel):
    """
    14-day forward-looking forecast.
    Used for the outlook chart on dashboard.
    """
    forecast_days: List[ForecastDay]
    avg_occupancy: float
    total_projected_revenue: Decimal
    peak_day: Optional[date]
    lowest_day: Optional[date]


class QuickStats(BaseModel):
    """
    Quick financial metrics for the header area.
    """
    revenue_today: Decimal
    revenue_mtd: Decimal  # Month to date
    revenue_ytd: Decimal  # Year to date
    avg_daily_rate: Decimal
    revpar: Decimal  # Revenue per available room
    occupancy_today: float

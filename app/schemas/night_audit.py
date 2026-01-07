"""
Pydantic schemas for Night Audit system.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# Night Audit Schemas
class NightAuditTrigger(BaseModel):
    """Request to trigger a night audit manually."""
    business_date: Optional[date] = None  # If None, uses current date
    notes: Optional[str] = None


class RoomChargeRead(BaseModel):
    """Room charge details from night audit."""
    id: int
    booking_id: int
    room_number: Optional[str] = None
    business_date: date
    room_rate: Decimal
    tax_amount: Decimal
    total_charge: Decimal
    is_posted: bool
    posted_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class NightAuditRead(BaseModel):
    """Night audit session details."""
    id: int
    business_date: date
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_completed: bool
    
    # Summary
    total_room_revenue: Decimal
    total_other_revenue: Decimal
    total_tax: Decimal
    total_payments: Decimal
    
    # Statistics
    rooms_occupied: int
    rooms_available: int
    rooms_out_of_service: int
    occupancy_percentage: Decimal
    
    # No-shows
    no_shows_processed: int
    no_show_revenue_lost: Decimal
    
    # Charges
    room_charges_posted: int
    
    # Details
    notes: Optional[str] = None
    errors: Optional[str] = None
    run_by_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NightAuditSummary(BaseModel):
    """Summary of night audit results."""
    business_date: date
    is_completed: bool
    
    # Revenue
    total_room_revenue: Decimal
    total_revenue: Decimal
    total_tax: Decimal
    
    # Occupancy
    occupancy_percentage: Decimal
    rooms_occupied: int
    rooms_available: int
    
    # Activity
    room_charges_posted: int
    no_shows_processed: int


class ReconciliationReport(BaseModel):
    """Daily reconciliation report."""
    business_date: date
    
    # Revenue breakdown
    room_revenue: Decimal
    other_revenue: Decimal
    total_revenue: Decimal
    total_tax: Decimal
    gross_total: Decimal
    
    # Payments
    total_payments: Decimal
    outstanding_balance: Decimal
    
    # Occupancy
    rooms_occupied: int
    rooms_available: int
    rooms_out_of_service: int
    occupancy_rate: Decimal
    average_daily_rate: Decimal
    revenue_per_available_room: Decimal
    
    # Activity
    arrivals: int
    departures: int
    stayovers: int
    no_shows: int
    
    # Charges posted
    room_charges_posted: int
    no_show_charges: int


class NoShowReport(BaseModel):
    """No-show processing report."""
    business_date: date
    total_no_shows: int
    revenue_lost: Decimal
    no_shows_charged: int
    no_shows_waived: int
    
    no_show_details: List[dict] = []  # List of booking IDs and amounts

"""
Night Audit model for tracking daily audit sessions and reconciliation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import date

from app.core.database import Base


class NightAudit(Base):
    """
    Night Audit session tracking.
    Each record represents one audit run for a specific business date.
    """
    __tablename__ = "night_audits"

    id = Column(Integer, primary_key=True, index=True)
    business_date = Column(Date, nullable=False, unique=True, index=True)
    
    # Audit execution tracking
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Audit results summary
    total_room_revenue = Column(Numeric(12, 2), default=0)
    total_other_revenue = Column(Numeric(12, 2), default=0)
    total_tax = Column(Numeric(12, 2), default=0)
    total_payments = Column(Numeric(12, 2), default=0)
    
    # Room statistics
    rooms_occupied = Column(Integer, default=0)
    rooms_available = Column(Integer, default=0)
    rooms_out_of_service = Column(Integer, default=0)
    occupancy_percentage = Column(Numeric(5, 2), default=0)
    
    # No-show processing
    no_shows_processed = Column(Integer, default=0)
    no_show_revenue_lost = Column(Numeric(12, 2), default=0)
    
    # Rate posting
    room_charges_posted = Column(Integer, default=0)
    
    # Audit details and notes
    notes = Column(Text, nullable=True)
    errors = Column(Text, nullable=True)
    
    # User who ran the audit
    run_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    run_by = relationship("User", foreign_keys=[run_by_id])
    room_charges = relationship("RoomCharge", back_populates="night_audit")

    def __repr__(self):
        return f"<NightAudit date={self.business_date} completed={self.is_completed}>"


class RoomCharge(Base):
    """
    Daily room rate charges posted during night audit.
    One record per room per night.
    """
    __tablename__ = "room_charges"

    id = Column(Integer, primary_key=True, index=True)
    night_audit_id = Column(Integer, ForeignKey("night_audits.id"), nullable=False)
    
    # Booking and room details
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    room_number = Column(String(20), nullable=True)  # For reference
    
    # Charge details
    business_date = Column(Date, nullable=False, index=True)
    room_rate = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_charge = Column(Numeric(10, 2), nullable=False)
    
    # Status
    is_posted = Column(Boolean, default=True, nullable=False)
    posted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    night_audit = relationship("NightAudit", back_populates="room_charges")
    booking = relationship("Booking")

    def __repr__(self):
        return f"<RoomCharge booking={self.booking_id} date={self.business_date} amount={self.total_charge}>"

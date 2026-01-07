"""
Customer model for CRM functionality.
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Customer(Base):
    """Customer model for CRM and booking association."""
    
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    id_proof_type = Column(String(50), nullable=True)  # passport, driver_license, etc.
    id_proof_number = Column(String(100), nullable=True)
    
    # VIP and loyalty fields
    is_vip = Column(Boolean, default=False, nullable=False)
    vip_notes = Column(Text, nullable=True)  # Special preferences/requests
    lifetime_value = Column(Numeric(12, 2), default=0, nullable=False)  # Total spend
    total_stays = Column(Integer, default=0, nullable=False)
    
    # General notes and preferences
    notes = Column(Text, nullable=True)  # Staff notes about the guest
    preferences = Column(Text, nullable=True)  # Room preferences, dietary, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="customer", lazy="selectin")
    
    @property
    def total_balance_due(self) -> float:
        """Calculate total outstanding balance across all bookings."""
        return sum(booking.balance_due for booking in self.bookings)
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, email={self.email}, vip={self.is_vip})>"



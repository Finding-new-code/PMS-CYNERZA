"""
Allotment model for group reservations and inventory blocks.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Enum, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class AllotmentStatus(str, enum.Enum):
    """Status progression for group allotments."""
    LEAD = "lead"  # Initial inquiry
    TENTATIVE = "tentative"  # Soft hold, pending confirmation
    DEFINITE = "definite"  # Confirmed group block
    RELEASED = "released"  # Released back to inventory
    CANCELLED = "cancelled"


class Allotment(Base):
    """
    Allotment model for managing group reservations.
    
    Workflow:
    1. Lead: Initial inquiry from a group
    2. Tentative: Rooms held pending contract
    3. Definite: Contract signed, rooms confirmed
    4. Released: Unused rooms released after cutoff date
    """
    
    __tablename__ = "allotments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # Group name (e.g., "TechConf 2026")
    status = Column(Enum(AllotmentStatus), nullable=False, default=AllotmentStatus.LEAD)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    cutoff_date = Column(Date, nullable=True)  # Date when unreserved rooms are released
    
    # Contact information
    contact_name = Column(String(200), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    # Financial
    group_rate = Column(Numeric(10, 2), nullable=True)  # Negotiated rate
    deposit_required = Column(Numeric(10, 2), nullable=True)
    deposit_paid = Column(Numeric(10, 2), default=0)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    rooms = relationship("AllotmentRoom", back_populates="allotment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Allotment(id={self.id}, name={self.name}, status={self.status})>"


class AllotmentRoom(Base):
    """
    Day-wise room allocation for an allotment.
    Tracks blocked vs picked-up rooms per date and room type.
    """
    
    __tablename__ = "allotment_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    allotment_id = Column(Integer, ForeignKey("allotments.id"), nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    blocked_rooms = Column(Integer, nullable=False, default=0)  # Total rooms held
    picked_up_rooms = Column(Integer, nullable=False, default=0)  # Rooms actually booked
    
    # Relationships
    allotment = relationship("Allotment", back_populates="rooms")
    room_type = relationship("RoomType")
    
    def __repr__(self):
        return f"<AllotmentRoom(allotment_id={self.allotment_id}, date={self.date}, blocked={self.blocked_rooms}, picked_up={self.picked_up_rooms})>"

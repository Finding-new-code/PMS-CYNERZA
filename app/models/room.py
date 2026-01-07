"""
Room model for individual room tracking with housekeeping status.
Extends the RoomType inventory system with physical room management.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class RoomStatus(str, enum.Enum):
    """Physical room status for housekeeping."""
    DIRTY = "dirty"
    CLEAN = "clean"
    INSPECTED = "inspected"
    OUT_OF_ORDER = "out_of_order"  # Maintenance issues
    OUT_OF_SERVICE = "out_of_service"  # Temporarily unavailable


class OccupancyStatus(str, enum.Enum):
    """Room occupancy status."""
    VACANT = "vacant"
    OCCUPIED = "occupied"
    CHECKOUT = "checkout"  # Expecting checkout
    CHECKIN = "checkin"  # Expecting check-in
    STAYOVER = "stayover"  # Continues staying


class Room(Base):
    """
    Physical room entity for housekeeping tracking.
    Each room belongs to a RoomType and has its own status.
    """
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), unique=True, nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False)
    floor = Column(Integer, nullable=True)
    
    # Housekeeping status
    housekeeping_status = Column(
        Enum(RoomStatus), 
        default=RoomStatus.DIRTY, 
        nullable=False
    )
    occupancy_status = Column(
        Enum(OccupancyStatus),
        default=OccupancyStatus.VACANT,
        nullable=False
    )
    
    # Assignment
    assigned_housekeeper_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Priority and notes
    priority = Column(Integer, default=0)  # Higher = more urgent
    housekeeping_notes = Column(Text, nullable=True)
    
    # Status tracking
    last_cleaned_at = Column(DateTime(timezone=True), nullable=True)
    last_inspected_at = Column(DateTime(timezone=True), nullable=True)
    status_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Active flag
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    room_type = relationship("RoomType", back_populates="rooms")
    assigned_housekeeper = relationship("User", foreign_keys=[assigned_housekeeper_id])
    housekeeping_tasks = relationship("HousekeepingTask", back_populates="room")

    def __repr__(self):
        return f"<Room {self.room_number} ({self.housekeeping_status.value})>"

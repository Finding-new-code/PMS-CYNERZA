"""
RoomBlock model for managing inventory blocks (maintenance, holds, out-of-service).
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class BlockType(str, enum.Enum):
    """Types of room blocks."""
    MAINTENANCE = "maintenance"
    HOLD = "hold"  # Courtesy hold for potential bookings
    OUT_OF_SERVICE = "out_of_service"


class BlockStatus(str, enum.Enum):
    """Status of a room block."""
    ACTIVE = "active"
    RELEASED = "released"
    EXPIRED = "expired"
    CONVERTED = "converted"  # Converted to a booking


class RoomBlock(Base):
    """
    Room block model for tracking temporary inventory reductions.
    
    Use Cases:
    - Maintenance: Rooms under repair
    - Hold: Courtesy holds for potential group bookings
    - Out of Service: Rooms that are unusable
    """
    
    __tablename__ = "room_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    block_type = Column(Enum(BlockType), nullable=False)
    num_rooms = Column(Integer, nullable=False, default=1)
    reason = Column(String(500), nullable=True)
    status = Column(Enum(BlockStatus), nullable=False, default=BlockStatus.ACTIVE)
    release_date = Column(Date, nullable=True)  # For auto-release of holds
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    room_type = relationship("RoomType", back_populates="blocks")
    
    def __repr__(self):
        return f"<RoomBlock(id={self.id}, type={self.block_type}, rooms={self.num_rooms}, {self.start_date} to {self.end_date})>"

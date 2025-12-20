"""
RoomType model for hotel room categories.
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RoomType(Base):
    """Room type/category model (e.g., Suite, Deluxe, Luxury)."""
    
    __tablename__ = "room_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    total_rooms = Column(Integer, nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    inventory = relationship("Inventory", back_populates="room_type", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="room_type")
    
    def __repr__(self):
        return f"<RoomType(id={self.id}, name={self.name}, total_rooms={self.total_rooms})>"

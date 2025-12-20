"""
Inventory model for date-wise room availability tracking.
"""

from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Inventory(Base):
    """
    Date-wise inventory tracking for room types.
    Each record represents availability for a specific room type on a specific date.
    """
    
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    available_rooms = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Can be adjusted per date
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Unique constraint: one inventory record per room type per date
    __table_args__ = (
        UniqueConstraint('room_type_id', 'date', name='uq_room_type_date'),
    )
    
    # Relationships
    room_type = relationship("RoomType", back_populates="inventory")
    
    def __repr__(self):
        return f"<Inventory(room_type_id={self.room_type_id}, date={self.date}, available={self.available_rooms})>"

"""
HousekeepingTask model for tracking housekeeping assignments and tasks.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class TaskType(str, enum.Enum):
    """Type of housekeeping task."""
    CHECKOUT_CLEAN = "checkout_clean"  # Deep clean after checkout
    STAYOVER_CLEAN = "stayover_clean"  # Light clean during stay
    INSPECTION = "inspection"  # Supervisor inspection
    TURNDOWN = "turndown"  # Evening turndown service
    DEEP_CLEAN = "deep_clean"  # Scheduled deep cleaning


class TaskStatus(str, enum.Enum):
    """Status of a housekeeping task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Priority level of a task."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class HousekeepingTask(Base):
    """
    Housekeeping task assignment and tracking.
    Links rooms to housekeepers with task details.
    """
    __tablename__ = "housekeeping_tasks"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    
    # Task details
    task_type = Column(Enum(TaskType), nullable=False)
    task_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL, nullable=False)
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timing
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    completion_notes = Column(Text, nullable=True)
    
    # Inspection (if applicable)
    inspected_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    inspection_passed = Column(Boolean, nullable=True)
    inspection_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    room = relationship("Room", back_populates="housekeeping_tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    inspected_by = relationship("User", foreign_keys=[inspected_by_id])

    def __repr__(self):
        return f"<HousekeepingTask {self.id} - {self.task_type.value} ({self.task_status.value})>"

"""
Automation models for trigger-based guest communication.
Supports pre-arrival, in-stay, and post-stay automated messages.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class TriggerType(str, enum.Enum):
    """Types of automation triggers."""
    # Pre-arrival
    BOOKING_CONFIRMED = "booking_confirmed"
    PRE_ARRIVAL_3_DAY = "pre_arrival_3_day"
    PRE_ARRIVAL_1_DAY = "pre_arrival_1_day"
    
    # Arrival
    CHECK_IN_WELCOME = "check_in_welcome"
    
    # In-stay
    IN_STAY_DAY_2 = "in_stay_day_2"
    IN_STAY_SATISFACTION = "in_stay_satisfaction"
    
    # Departure
    PRE_CHECKOUT = "pre_checkout"
    
    # Post-stay
    POST_STAY_THANK_YOU = "post_stay_thank_you"
    POST_STAY_REVIEW = "post_stay_review"
    
    # Custom
    CUSTOM = "custom"


class AutomationStatus(str, enum.Enum):
    """Automation rule status."""
    ACTIVE = "active"
    PAUSED = "paused"
    DRAFT = "draft"


class AutomationRule(Base):
    """
    Automation rule definition.
    Defines when and what message to send automatically.
    """
    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Rule info
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    
    # Trigger configuration
    trigger_type = Column(Enum(TriggerType), nullable=False, index=True)
    trigger_delay_hours = Column(Integer, default=0)  # Delay after trigger event
    trigger_time = Column(String(5), nullable=True)  # "09:00" - specific time to send
    
    # Message template
    template_id = Column(Integer, ForeignKey("message_templates.id"), nullable=False)
    
    # Conditions (JSON for flexible filtering)
    conditions = Column(Text, nullable=True)  # {"room_type": "suite", "is_vip": true}
    
    # Status
    status = Column(Enum(AutomationStatus), default=AutomationStatus.DRAFT)
    is_enabled = Column(Boolean, default=True, nullable=False)
    
    # Stats
    times_triggered = Column(Integer, default=0)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    template = relationship("MessageTemplate")
    created_by = relationship("User")

    def __repr__(self):
        return f"<AutomationRule {self.name} ({self.trigger_type.value})>"


class AutomationLog(Base):
    """
    Log of automation executions.
    Tracks when automations were triggered and their results.
    """
    __tablename__ = "automation_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    rule_id = Column(Integer, ForeignKey("automation_rules.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Execution details
    trigger_type = Column(Enum(TriggerType), nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    was_successful = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    metadata = Column(Text, nullable=True)  # JSON for additional context
    
    # Relationships
    rule = relationship("AutomationRule")
    booking = relationship("Booking")
    customer = relationship("Customer")
    message = relationship("Message")

    def __repr__(self):
        return f"<AutomationLog {self.id} rule={self.rule_id}>"

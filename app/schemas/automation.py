"""
Pydantic schemas for Automation Engine.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TriggerTypeEnum(str, Enum):
    BOOKING_CONFIRMED = "booking_confirmed"
    PRE_ARRIVAL_3_DAY = "pre_arrival_3_day"
    PRE_ARRIVAL_1_DAY = "pre_arrival_1_day"
    CHECK_IN_WELCOME = "check_in_welcome"
    IN_STAY_DAY_2 = "in_stay_day_2"
    IN_STAY_SATISFACTION = "in_stay_satisfaction"
    PRE_CHECKOUT = "pre_checkout"
    POST_STAY_THANK_YOU = "post_stay_thank_you"
    POST_STAY_REVIEW = "post_stay_review"
    CUSTOM = "custom"


class AutomationStatusEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DRAFT = "draft"


# Automation Rule Schemas
class AutomationRuleCreate(BaseModel):
    """Create an automation rule."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    trigger_type: TriggerTypeEnum
    trigger_delay_hours: int = 0
    trigger_time: Optional[str] = None  # "09:00"
    template_id: int
    conditions: Optional[Dict[str, Any]] = None
    status: AutomationStatusEnum = AutomationStatusEnum.DRAFT


class AutomationRuleUpdate(BaseModel):
    """Update automation rule."""
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_delay_hours: Optional[int] = None
    trigger_time: Optional[str] = None
    template_id: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None
    status: Optional[AutomationStatusEnum] = None
    is_enabled: Optional[bool] = None


class AutomationRuleRead(BaseModel):
    """Automation rule response."""
    id: int
    name: str
    description: Optional[str] = None
    trigger_type: TriggerTypeEnum
    trigger_delay_hours: int
    trigger_time: Optional[str] = None
    template_id: int
    template_name: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    status: AutomationStatusEnum
    is_enabled: bool
    times_triggered: int
    last_triggered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Automation Log Schemas
class AutomationLogRead(BaseModel):
    """Automation execution log."""
    id: int
    rule_id: int
    rule_name: Optional[str] = None
    booking_id: Optional[int] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    message_id: Optional[int] = None
    trigger_type: TriggerTypeEnum
    triggered_at: datetime
    executed_at: Optional[datetime] = None
    was_successful: bool
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# Manual Trigger
class ManualTrigger(BaseModel):
    """Manually trigger automation for a booking."""
    rule_id: int
    booking_id: int


# Automation Summary
class AutomationSummary(BaseModel):
    """Automation dashboard summary."""
    total_rules: int
    active_rules: int
    paused_rules: int
    triggers_today: int
    success_rate: float  # Percentage
    by_trigger_type: Dict[str, int]

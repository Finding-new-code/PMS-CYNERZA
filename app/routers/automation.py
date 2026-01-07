"""
Automation API router for trigger-based guest communication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.automation import (
    AutomationRuleCreate, AutomationRuleUpdate, AutomationRuleRead,
    AutomationLogRead, ManualTrigger, AutomationSummary,
    TriggerTypeEnum, AutomationStatusEnum
)
from app.services import automation_service
from app.models.automation import TriggerType, AutomationStatus
from app.models.booking import Booking
from app.models.customer import Customer
from sqlalchemy import select
import json

router = APIRouter(prefix="/automation", tags=["Automation"])


# ============ Rules ============

@router.post("/rules", response_model=AutomationRuleRead, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: AutomationRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new automation rule."""
    data = rule_data.model_dump()
    data["created_by_id"] = current_user.id
    data["trigger_type"] = TriggerType(rule_data.trigger_type.value)
    data["status"] = AutomationStatus(rule_data.status.value)
    
    rule = await automation_service.create_rule(db, data)
    
    conditions = None
    if rule.conditions:
        try:
            conditions = json.loads(rule.conditions)
        except:
            conditions = None
    
    return AutomationRuleRead(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger_type=TriggerTypeEnum(rule.trigger_type.value),
        trigger_delay_hours=rule.trigger_delay_hours,
        trigger_time=rule.trigger_time,
        template_id=rule.template_id,
        template_name=rule.template.name if rule.template else None,
        conditions=conditions,
        status=AutomationStatusEnum(rule.status.value),
        is_enabled=rule.is_enabled,
        times_triggered=rule.times_triggered,
        last_triggered_at=rule.last_triggered_at,
        created_at=rule.created_at
    )


@router.get("/rules", response_model=List[AutomationRuleRead])
async def list_rules(
    trigger_type: Optional[TriggerTypeEnum] = Query(None),
    status: Optional[AutomationStatusEnum] = Query(None),
    enabled_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get automation rules with filters."""
    type_filter = TriggerType(trigger_type.value) if trigger_type else None
    status_filter = AutomationStatus(status.value) if status else None
    
    rules = await automation_service.get_rules(
        db, type_filter, status_filter, enabled_only
    )
    
    result = []
    for rule in rules:
        conditions = None
        if rule.conditions:
            try:
                conditions = json.loads(rule.conditions)
            except:
                conditions = None
        
        result.append(AutomationRuleRead(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            trigger_type=TriggerTypeEnum(rule.trigger_type.value),
            trigger_delay_hours=rule.trigger_delay_hours,
            trigger_time=rule.trigger_time,
            template_id=rule.template_id,
            template_name=rule.template.name if rule.template else None,
            conditions=conditions,
            status=AutomationStatusEnum(rule.status.value),
            is_enabled=rule.is_enabled,
            times_triggered=rule.times_triggered,
            last_triggered_at=rule.last_triggered_at,
            created_at=rule.created_at
        ))
    
    return result


@router.get("/rules/{rule_id}", response_model=AutomationRuleRead)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific automation rule."""
    rule = await automation_service.get_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    conditions = None
    if rule.conditions:
        try:
            conditions = json.loads(rule.conditions)
        except:
            conditions = None
    
    return AutomationRuleRead(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger_type=TriggerTypeEnum(rule.trigger_type.value),
        trigger_delay_hours=rule.trigger_delay_hours,
        trigger_time=rule.trigger_time,
        template_id=rule.template_id,
        template_name=rule.template.name if rule.template else None,
        conditions=conditions,
        status=AutomationStatusEnum(rule.status.value),
        is_enabled=rule.is_enabled,
        times_triggered=rule.times_triggered,
        last_triggered_at=rule.last_triggered_at,
        created_at=rule.created_at
    )


@router.patch("/rules/{rule_id}", response_model=AutomationRuleRead)
async def update_rule(
    rule_id: int,
    updates: AutomationRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an automation rule."""
    update_data = updates.model_dump(exclude_unset=True)
    
    if "status" in update_data and update_data["status"]:
        update_data["status"] = AutomationStatus(update_data["status"].value)
    
    rule = await automation_service.update_rule(db, rule_id, update_data)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    conditions = None
    if rule.conditions:
        try:
            conditions = json.loads(rule.conditions)
        except:
            conditions = None
    
    return AutomationRuleRead(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger_type=TriggerTypeEnum(rule.trigger_type.value),
        trigger_delay_hours=rule.trigger_delay_hours,
        trigger_time=rule.trigger_time,
        template_id=rule.template_id,
        template_name=rule.template.name if rule.template else None,
        conditions=conditions,
        status=AutomationStatusEnum(rule.status.value),
        is_enabled=rule.is_enabled,
        times_triggered=rule.times_triggered,
        last_triggered_at=rule.last_triggered_at,
        created_at=rule.created_at
    )


# ============ Manual Trigger ============

@router.post("/trigger")
async def manual_trigger(
    trigger_data: ManualTrigger,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger an automation for a booking."""
    rule = await automation_service.get_rule(db, trigger_data.rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Get booking
    booking_query = select(Booking).where(Booking.id == trigger_data.booking_id)
    booking = (await db.execute(booking_query)).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get customer
    customer_query = select(Customer).where(Customer.id == booking.customer_id)
    customer = (await db.execute(customer_query)).scalar_one_or_none()
    
    log = await automation_service.trigger_automation(db, rule, booking, customer)
    
    return {
        "message": "Automation triggered",
        "success": log.was_successful,
        "log_id": log.id,
        "message_id": log.message_id
    }


# ============ Logs ============

@router.get("/logs", response_model=List[AutomationLogRead])
async def list_logs(
    rule_id: Optional[int] = Query(None),
    booking_id: Optional[int] = Query(None),
    successful_only: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get automation execution logs."""
    logs = await automation_service.get_logs(
        db, rule_id, booking_id, successful_only, limit, offset
    )
    
    return [
        AutomationLogRead(
            id=log.id,
            rule_id=log.rule_id,
            rule_name=log.rule.name if log.rule else None,
            booking_id=log.booking_id,
            customer_id=log.customer_id,
            customer_name=log.customer.name if log.customer else None,
            message_id=log.message_id,
            trigger_type=TriggerTypeEnum(log.trigger_type.value),
            triggered_at=log.triggered_at,
            executed_at=log.executed_at,
            was_successful=log.was_successful,
            error_message=log.error_message
        )
        for log in logs
    ]


# ============ Summary ============

@router.get("/summary", response_model=AutomationSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get automation dashboard summary."""
    summary = await automation_service.get_automation_summary(db)
    return AutomationSummary(**summary)

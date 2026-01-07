"""
Automation service for trigger-based guest communication.
Handles pre-arrival, in-stay, and post-stay automated messaging.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json

from app.models.automation import AutomationRule, AutomationLog, TriggerType, AutomationStatus
from app.models.booking import Booking, BookingStatus
from app.models.customer import Customer
from app.services import messaging_service
from app.models.messaging import MessageChannel


async def create_rule(db: AsyncSession, rule_data: dict) -> AutomationRule:
    """Create a new automation rule."""
    # Convert conditions dict to JSON
    if "conditions" in rule_data and isinstance(rule_data["conditions"], dict):
        rule_data["conditions"] = json.dumps(rule_data["conditions"])
    
    rule = AutomationRule(**rule_data)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


async def get_rule(db: AsyncSession, rule_id: int) -> Optional[AutomationRule]:
    """Get an automation rule by ID."""
    query = select(AutomationRule).options(
        selectinload(AutomationRule.template)
    ).where(AutomationRule.id == rule_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_rules(
    db: AsyncSession,
    trigger_type: Optional[TriggerType] = None,
    status: Optional[AutomationStatus] = None,
    enabled_only: bool = False
) -> List[AutomationRule]:
    """Get automation rules with filters."""
    query = select(AutomationRule).options(
        selectinload(AutomationRule.template)
    )
    
    if trigger_type:
        query = query.where(AutomationRule.trigger_type == trigger_type)
    if status:
        query = query.where(AutomationRule.status == status)
    if enabled_only:
        query = query.where(AutomationRule.is_enabled == True)
    
    query = query.order_by(AutomationRule.name)
    result = await db.execute(query)
    return result.scalars().all()


async def update_rule(
    db: AsyncSession,
    rule_id: int,
    updates: dict
) -> Optional[AutomationRule]:
    """Update an automation rule."""
    rule = await get_rule(db, rule_id)
    if not rule:
        return None
    
    # Convert conditions dict to JSON
    if "conditions" in updates and isinstance(updates["conditions"], dict):
        updates["conditions"] = json.dumps(updates["conditions"])
    
    for key, value in updates.items():
        if value is not None and hasattr(rule, key):
            setattr(rule, key, value)
    
    await db.commit()
    await db.refresh(rule)
    return rule


async def trigger_automation(
    db: AsyncSession,
    rule: AutomationRule,
    booking: Booking,
    customer: Customer
) -> AutomationLog:
    """
    Execute an automation for a specific booking/customer.
    Creates a message using the rule's template.
    """
    log = AutomationLog(
        rule_id=rule.id,
        booking_id=booking.id if booking else None,
        customer_id=customer.id if customer else None,
        trigger_type=rule.trigger_type,
        triggered_at=datetime.utcnow()
    )
    db.add(log)
    
    try:
        # Build template variables
        variables = {
            "guest_name": customer.name if customer else "Guest",
            "check_in_date": str(booking.check_in) if booking else "",
            "check_out_date": str(booking.check_out) if booking else "",
            "booking_id": str(booking.id) if booking else "",
        }
        
        # Render template
        rendered = await messaging_service.render_template(
            db, rule.template_id, variables
        )
        
        # Create and send message
        message = await messaging_service.create_message(
            db,
            channel=rule.template.channel if rule.template else MessageChannel.EMAIL,
            body=rendered["body"],
            subject=rendered.get("subject"),
            body_html=rendered.get("body_html"),
            customer_id=customer.id if customer else None,
            booking_id=booking.id if booking else None,
            template_id=rule.template_id
        )
        
        # Send the message
        await messaging_service.send_message(db, message.id)
        
        # Update log
        log.message_id = message.id
        log.executed_at = datetime.utcnow()
        log.was_successful = True
        
        # Update rule stats
        rule.times_triggered += 1
        rule.last_triggered_at = datetime.utcnow()
        
    except Exception as e:
        log.was_successful = False
        log.error_message = str(e)
    
    await db.commit()
    await db.refresh(log)
    return log


async def process_scheduled_triggers(db: AsyncSession, trigger_type: TriggerType) -> List[AutomationLog]:
    """
    Process all pending automations for a specific trigger type.
    Called by scheduler for time-based triggers.
    """
    # Get active rules for this trigger type
    rules = await get_rules(db, trigger_type=trigger_type, status=AutomationStatus.ACTIVE, enabled_only=True)
    
    if not rules:
        return []
    
    logs = []
    today = date.today()
    
    for rule in rules:
        # Find applicable bookings based on trigger type
        bookings = await get_bookings_for_trigger(db, trigger_type, today)
        
        for booking in bookings:
            # Check if already triggered for this booking
            existing = await db.execute(
                select(AutomationLog).where(
                    and_(
                        AutomationLog.rule_id == rule.id,
                        AutomationLog.booking_id == booking.id
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip if already triggered
            
            # Get customer
            customer_query = select(Customer).where(Customer.id == booking.customer_id)
            customer = (await db.execute(customer_query)).scalar_one_or_none()
            
            # Trigger the automation
            log = await trigger_automation(db, rule, booking, customer)
            logs.append(log)
    
    return logs


async def get_bookings_for_trigger(
    db: AsyncSession,
    trigger_type: TriggerType,
    reference_date: date
) -> List[Booking]:
    """Get bookings that match a trigger type."""
    query = select(Booking)
    
    if trigger_type == TriggerType.PRE_ARRIVAL_3_DAY:
        check_in_date = reference_date + timedelta(days=3)
        query = query.where(Booking.check_in == check_in_date)
    
    elif trigger_type == TriggerType.PRE_ARRIVAL_1_DAY:
        check_in_date = reference_date + timedelta(days=1)
        query = query.where(Booking.check_in == check_in_date)
    
    elif trigger_type == TriggerType.CHECK_IN_WELCOME:
        query = query.where(
            and_(
                Booking.check_in == reference_date,
                Booking.status == BookingStatus.CONFIRMED
            )
        )
    
    elif trigger_type == TriggerType.POST_STAY_THANK_YOU:
        check_out_date = reference_date - timedelta(days=1)
        query = query.where(Booking.check_out == check_out_date)
    
    elif trigger_type == TriggerType.POST_STAY_REVIEW:
        # 3 days after checkout
        check_out_date = reference_date - timedelta(days=3)
        query = query.where(Booking.check_out == check_out_date)
    
    else:
        return []
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_logs(
    db: AsyncSession,
    rule_id: Optional[int] = None,
    booking_id: Optional[int] = None,
    successful_only: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> List[AutomationLog]:
    """Get automation execution logs."""
    query = select(AutomationLog).options(
        selectinload(AutomationLog.rule),
        selectinload(AutomationLog.customer)
    )
    
    if rule_id:
        query = query.where(AutomationLog.rule_id == rule_id)
    if booking_id:
        query = query.where(AutomationLog.booking_id == booking_id)
    if successful_only is not None:
        query = query.where(AutomationLog.was_successful == successful_only)
    
    query = query.order_by(AutomationLog.triggered_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_automation_summary(db: AsyncSession) -> dict:
    """Get automation dashboard summary."""
    # Total rules
    total_query = select(func.count(AutomationRule.id))
    total = (await db.execute(total_query)).scalar() or 0
    
    # Active rules
    active_query = select(func.count(AutomationRule.id)).where(
        AutomationRule.status == AutomationStatus.ACTIVE
    )
    active = (await db.execute(active_query)).scalar() or 0
    
    # Paused rules
    paused_query = select(func.count(AutomationRule.id)).where(
        AutomationRule.status == AutomationStatus.PAUSED
    )
    paused = (await db.execute(paused_query)).scalar() or 0
    
    # Triggers today
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_query = select(func.count(AutomationLog.id)).where(
        AutomationLog.triggered_at >= today_start
    )
    triggers_today = (await db.execute(today_query)).scalar() or 0
    
    # Success rate (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    success_query = select(
        func.count(AutomationLog.id).filter(AutomationLog.was_successful == True),
        func.count(AutomationLog.id)
    ).where(AutomationLog.triggered_at >= thirty_days_ago)
    
    success_result = await db.execute(success_query)
    row = success_result.one()
    success_count, total_count = row[0] or 0, row[1] or 0
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    # By trigger type
    by_type_query = select(
        AutomationRule.trigger_type,
        func.count(AutomationRule.id)
    ).group_by(AutomationRule.trigger_type)
    
    type_result = await db.execute(by_type_query)
    by_trigger_type = {row[0].value: row[1] for row in type_result}
    
    return {
        "total_rules": total,
        "active_rules": active,
        "paused_rules": paused,
        "triggers_today": triggers_today,
        "success_rate": round(success_rate, 2),
        "by_trigger_type": by_trigger_type
    }

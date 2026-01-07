"""
Messaging API router for unified inbox and communication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.messaging import (
    MessageCreate, MessageRead, MessageSend,
    TemplateCreate, TemplateUpdate, TemplateRead, TemplateRender,
    ConversationRead, InboxSummary,
    MessageChannelEnum, MessageDirectionEnum, MessageStatusEnum
)
from app.services import messaging_service
from app.models.messaging import MessageChannel, MessageDirection
import json

router = APIRouter(prefix="/messaging", tags=["Messaging"])


# ============ Messages ============

@router.post("/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new outbound message."""
    message = await messaging_service.create_message(
        db,
        channel=MessageChannel(message_data.channel.value),
        body=message_data.body,
        direction=MessageDirection.OUTBOUND,
        sender_user_id=current_user.id,
        customer_id=message_data.customer_id,
        booking_id=message_data.booking_id,
        recipient_email=message_data.recipient_email,
        recipient_phone=message_data.recipient_phone,
        subject=message_data.subject,
        body_html=message_data.body_html,
        template_id=message_data.template_id,
        thread_id=message_data.thread_id
    )
    
    return MessageRead(
        id=message.id,
        channel=MessageChannelEnum(message.channel.value),
        direction=MessageDirectionEnum(message.direction.value),
        status=MessageStatusEnum(message.status.value),
        booking_id=message.booking_id,
        customer_id=message.customer_id,
        customer_name=message.customer.name if message.customer else None,
        recipient_email=message.recipient_email,
        recipient_phone=message.recipient_phone,
        subject=message.subject,
        body=message.body,
        template_id=message.template_id,
        thread_id=message.thread_id,
        is_read=message.is_read,
        read_at=message.read_at,
        scheduled_at=message.scheduled_at,
        sent_at=message.sent_at,
        created_at=message.created_at
    )


@router.post("/messages/{message_id}/send")
async def send_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message."""
    try:
        message = await messaging_service.send_message(db, message_id)
        return {"message": "Message sent", "sent_at": message.sent_at}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/messages", response_model=List[MessageRead])
async def list_messages(
    channel: Optional[MessageChannelEnum] = Query(None),
    direction: Optional[MessageDirectionEnum] = Query(None),
    customer_id: Optional[int] = Query(None),
    booking_id: Optional[int] = Query(None),
    thread_id: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages with filters."""
    channel_filter = MessageChannel(channel.value) if channel else None
    direction_filter = MessageDirection(direction.value) if direction else None
    
    messages = await messaging_service.get_messages(
        db, channel_filter, direction_filter,
        customer_id, booking_id, thread_id,
        unread_only, limit, offset
    )
    
    return [
        MessageRead(
            id=m.id,
            channel=MessageChannelEnum(m.channel.value),
            direction=MessageDirectionEnum(m.direction.value),
            status=MessageStatusEnum(m.status.value),
            booking_id=m.booking_id,
            customer_id=m.customer_id,
            customer_name=m.customer.name if m.customer else None,
            recipient_email=m.recipient_email,
            recipient_phone=m.recipient_phone,
            subject=m.subject,
            body=m.body,
            template_id=m.template_id,
            thread_id=m.thread_id,
            is_read=m.is_read,
            read_at=m.read_at,
            scheduled_at=m.scheduled_at,
            sent_at=m.sent_at,
            created_at=m.created_at
        )
        for m in messages
    ]


@router.post("/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a message as read."""
    message = await messaging_service.mark_as_read(db, message_id, current_user.id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Marked as read", "read_at": message.read_at}


# ============ Templates ============

@router.post("/templates", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new message template."""
    data = template_data.model_dump()
    data["created_by_id"] = current_user.id
    data["channel"] = MessageChannel(template_data.channel.value)
    
    template = await messaging_service.create_template(db, data)
    
    variables = None
    if template.variables:
        try:
            variables = json.loads(template.variables)
        except:
            variables = None
    
    return TemplateRead(
        id=template.id,
        name=template.name,
        description=template.description,
        category=template.category,
        channel=MessageChannelEnum(template.channel.value),
        subject=template.subject,
        body=template.body,
        body_html=template.body_html,
        language=template.language,
        variables=variables,
        is_active=template.is_active,
        created_at=template.created_at
    )


@router.get("/templates", response_model=List[TemplateRead])
async def list_templates(
    channel: Optional[MessageChannelEnum] = Query(None),
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get message templates."""
    channel_filter = MessageChannel(channel.value) if channel else None
    templates = await messaging_service.get_templates(
        db, channel_filter, category, active_only
    )
    
    result = []
    for t in templates:
        variables = None
        if t.variables:
            try:
                variables = json.loads(t.variables)
            except:
                variables = None
        
        result.append(TemplateRead(
            id=t.id,
            name=t.name,
            description=t.description,
            category=t.category,
            channel=MessageChannelEnum(t.channel.value),
            subject=t.subject,
            body=t.body,
            body_html=t.body_html,
            language=t.language,
            variables=variables,
            is_active=t.is_active,
            created_at=t.created_at
        ))
    
    return result


@router.post("/templates/render")
async def render_template(
    render_data: TemplateRender,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Render a template with variables."""
    try:
        rendered = await messaging_service.render_template(
            db, render_data.template_id, render_data.variables
        )
        return rendered
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============ Conversations ============

@router.get("/conversations", response_model=List[ConversationRead])
async def list_conversations(
    is_open: Optional[bool] = Query(None),
    is_starred: Optional[bool] = Query(None),
    assigned_to: Optional[int] = Query(None),
    channel: Optional[MessageChannelEnum] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation threads."""
    channel_filter = MessageChannel(channel.value) if channel else None
    
    conversations = await messaging_service.get_conversations(
        db, is_open, is_starred, assigned_to,
        channel_filter, limit, offset
    )
    
    return [
        ConversationRead(
            id=c.id,
            thread_id=c.thread_id,
            customer_id=c.customer_id,
            customer_name=c.customer.name if c.customer else None,
            booking_id=c.booking_id,
            primary_channel=MessageChannelEnum(c.primary_channel.value),
            is_open=c.is_open,
            is_starred=c.is_starred,
            assigned_to_id=c.assigned_to_id,
            assigned_to_name=c.assigned_to.email if c.assigned_to else None,
            message_count=c.message_count,
            unread_count=c.unread_count,
            last_message_at=c.last_message_at,
            created_at=c.created_at
        )
        for c in conversations
    ]


# ============ Inbox Summary ============

@router.get("/inbox/summary", response_model=InboxSummary)
async def get_inbox_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unified inbox summary."""
    summary = await messaging_service.get_inbox_summary(db)
    return InboxSummary(**summary)

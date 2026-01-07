"""
Messaging service for unified inbox, templates, and communication.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json
import re
import uuid

from app.models.messaging import (
    Message, MessageTemplate, Conversation,
    MessageChannel, MessageDirection, MessageStatus
)


async def create_conversation(
    db: AsyncSession,
    customer_id: Optional[int],
    booking_id: Optional[int],
    channel: MessageChannel
) -> Conversation:
    """Create a new conversation thread."""
    thread_id = f"conv_{uuid.uuid4().hex[:12]}"
    
    conversation = Conversation(
        thread_id=thread_id,
        customer_id=customer_id,
        booking_id=booking_id,
        primary_channel=channel,
        is_open=True,
        message_count=0,
        unread_count=0
    )
    db.add(conversation)
    await db.flush()
    return conversation


async def get_or_create_conversation(
    db: AsyncSession,
    customer_id: Optional[int] = None,
    booking_id: Optional[int] = None,
    channel: MessageChannel = MessageChannel.EMAIL
) -> Conversation:
    """Get existing conversation or create new one."""
    # Try to find existing open conversation
    query = select(Conversation).where(Conversation.is_open == True)
    
    if customer_id:
        query = query.where(Conversation.customer_id == customer_id)
    if booking_id:
        query = query.where(Conversation.booking_id == booking_id)
    
    result = await db.execute(query.order_by(Conversation.created_at.desc()).limit(1))
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        conversation = await create_conversation(db, customer_id, booking_id, channel)
    
    return conversation


async def create_message(
    db: AsyncSession,
    channel: MessageChannel,
    body: str,
    direction: MessageDirection = MessageDirection.OUTBOUND,
    sender_user_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    booking_id: Optional[int] = None,
    recipient_email: Optional[str] = None,
    recipient_phone: Optional[str] = None,
    subject: Optional[str] = None,
    body_html: Optional[str] = None,
    template_id: Optional[int] = None,
    thread_id: Optional[str] = None
) -> Message:
    """Create a new message."""
    # Get or create conversation
    if not thread_id:
        conversation = await get_or_create_conversation(
            db, customer_id, booking_id, channel
        )
        thread_id = conversation.thread_id
    
    message = Message(
        channel=channel,
        direction=direction,
        status=MessageStatus.DRAFT,
        booking_id=booking_id,
        customer_id=customer_id,
        sender_user_id=sender_user_id,
        recipient_email=recipient_email,
        recipient_phone=recipient_phone,
        subject=subject,
        body=body,
        body_html=body_html,
        template_id=template_id,
        thread_id=thread_id
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def send_message(db: AsyncSession, message_id: int) -> Message:
    """
    Send a message (mark as sent).
    In production, this would integrate with email/SMS providers.
    """
    query = select(Message).where(Message.id == message_id)
    result = await db.execute(query)
    message = result.scalar_one_or_none()
    
    if not message:
        raise ValueError("Message not found")
    
    message.status = MessageStatus.SENT
    message.sent_at = datetime.utcnow()
    
    # Update conversation
    if message.thread_id:
        conv_query = select(Conversation).where(
            Conversation.thread_id == message.thread_id
        )
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if conversation:
            conversation.message_count += 1
            conversation.last_message_at = datetime.utcnow()
            if message.direction == MessageDirection.INBOUND:
                conversation.unread_count += 1
    
    await db.commit()
    await db.refresh(message)
    return message


async def get_messages(
    db: AsyncSession,
    channel: Optional[MessageChannel] = None,
    direction: Optional[MessageDirection] = None,
    customer_id: Optional[int] = None,
    booking_id: Optional[int] = None,
    thread_id: Optional[str] = None,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0
) -> List[Message]:
    """Get messages with filters."""
    query = select(Message).options(
        selectinload(Message.customer),
        selectinload(Message.booking)
    )
    
    if channel:
        query = query.where(Message.channel == channel)
    if direction:
        query = query.where(Message.direction == direction)
    if customer_id:
        query = query.where(Message.customer_id == customer_id)
    if booking_id:
        query = query.where(Message.booking_id == booking_id)
    if thread_id:
        query = query.where(Message.thread_id == thread_id)
    if unread_only:
        query = query.where(Message.is_read == False)
    
    query = query.order_by(Message.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def mark_as_read(db: AsyncSession, message_id: int, user_id: int) -> Message:
    """Mark a message as read."""
    query = select(Message).where(Message.id == message_id)
    result = await db.execute(query)
    message = result.scalar_one_or_none()
    
    if message and not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        message.read_by_id = user_id
        
        # Update conversation unread count
        if message.thread_id:
            conv_query = select(Conversation).where(
                Conversation.thread_id == message.thread_id
            )
            conv_result = await db.execute(conv_query)
            conversation = conv_result.scalar_one_or_none()
            
            if conversation and conversation.unread_count > 0:
                conversation.unread_count -= 1
        
        await db.commit()
        await db.refresh(message)
    
    return message


# Template Functions
async def create_template(db: AsyncSession, template_data: dict) -> MessageTemplate:
    """Create a message template."""
    # Convert variables list to JSON if provided
    if "variables" in template_data and isinstance(template_data["variables"], list):
        template_data["variables"] = json.dumps(template_data["variables"])
    
    template = MessageTemplate(**template_data)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def get_templates(
    db: AsyncSession,
    channel: Optional[MessageChannel] = None,
    category: Optional[str] = None,
    active_only: bool = True
) -> List[MessageTemplate]:
    """Get message templates with filters."""
    query = select(MessageTemplate)
    
    if channel:
        query = query.where(MessageTemplate.channel == channel)
    if category:
        query = query.where(MessageTemplate.category == category)
    if active_only:
        query = query.where(MessageTemplate.is_active == True)
    
    query = query.order_by(MessageTemplate.name)
    result = await db.execute(query)
    return result.scalars().all()


async def render_template(
    db: AsyncSession,
    template_id: int,
    variables: Dict[str, Any]
) -> Dict[str, str]:
    """
    Render a template with provided variables.
    Replaces {{variable_name}} with actual values.
    """
    query = select(MessageTemplate).where(MessageTemplate.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise ValueError("Template not found")
    
    def replace_vars(text: str, vars: Dict[str, Any]) -> str:
        if not text:
            return text
        for key, value in vars.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
        return text
    
    return {
        "subject": replace_vars(template.subject, variables) if template.subject else None,
        "body": replace_vars(template.body, variables),
        "body_html": replace_vars(template.body_html, variables) if template.body_html else None
    }


# Conversation Functions
async def get_conversations(
    db: AsyncSession,
    is_open: Optional[bool] = None,
    is_starred: Optional[bool] = None,
    assigned_to: Optional[int] = None,
    channel: Optional[MessageChannel] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Conversation]:
    """Get conversations with filters."""
    query = select(Conversation).options(
        selectinload(Conversation.customer),
        selectinload(Conversation.assigned_to)
    )
    
    if is_open is not None:
        query = query.where(Conversation.is_open == is_open)
    if is_starred:
        query = query.where(Conversation.is_starred == True)
    if assigned_to:
        query = query.where(Conversation.assigned_to_id == assigned_to)
    if channel:
        query = query.where(Conversation.primary_channel == channel)
    
    query = query.order_by(Conversation.last_message_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_inbox_summary(db: AsyncSession) -> dict:
    """Get unified inbox summary statistics."""
    # Total conversations
    total_query = select(func.count(Conversation.id))
    total = (await db.execute(total_query)).scalar() or 0
    
    # Open conversations
    open_query = select(func.count(Conversation.id)).where(
        Conversation.is_open == True
    )
    open_count = (await db.execute(open_query)).scalar() or 0
    
    # Unread messages
    unread_query = select(func.count(Message.id)).where(
        and_(
            Message.is_read == False,
            Message.direction == MessageDirection.INBOUND
        )
    )
    unread = (await db.execute(unread_query)).scalar() or 0
    
    # Starred
    starred_query = select(func.count(Conversation.id)).where(
        Conversation.is_starred == True
    )
    starred = (await db.execute(starred_query)).scalar() or 0
    
    # By channel
    channel_query = select(
        Conversation.primary_channel,
        func.count(Conversation.id)
    ).where(Conversation.is_open == True).group_by(Conversation.primary_channel)
    
    channel_result = await db.execute(channel_query)
    by_channel = {row[0].value: row[1] for row in channel_result}
    
    return {
        "total_conversations": total,
        "open_conversations": open_count,
        "unread_messages": unread,
        "starred": starred,
        "by_channel": by_channel
    }

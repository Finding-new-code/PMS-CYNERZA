"""
Pydantic schemas for Messaging System.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageChannelEnum(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    INTERNAL = "internal"
    PUSH = "push"


class MessageDirectionEnum(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageStatusEnum(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


# Message Schemas
class MessageCreate(BaseModel):
    """Create a new message."""
    channel: MessageChannelEnum
    booking_id: Optional[int] = None
    customer_id: Optional[int] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    subject: Optional[str] = None
    body: str
    body_html: Optional[str] = None
    template_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    thread_id: Optional[str] = None


class MessageSend(BaseModel):
    """Send message immediately or schedule."""
    message_id: int
    send_now: bool = True
    scheduled_at: Optional[datetime] = None


class MessageRead(BaseModel):
    """Message response."""
    id: int
    channel: MessageChannelEnum
    direction: MessageDirectionEnum
    status: MessageStatusEnum
    booking_id: Optional[int] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    subject: Optional[str] = None
    body: str
    template_id: Optional[int] = None
    thread_id: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Template Schemas
class TemplateCreate(BaseModel):
    """Create a message template."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    channel: MessageChannelEnum
    subject: Optional[str] = None
    body: str
    body_html: Optional[str] = None
    language: str = "en"
    variables: Optional[List[str]] = None


class TemplateUpdate(BaseModel):
    """Update a template."""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    body_html: Optional[str] = None
    language: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TemplateRead(BaseModel):
    """Template response."""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    channel: MessageChannelEnum
    subject: Optional[str] = None
    body: str
    body_html: Optional[str] = None
    language: str
    variables: Optional[List[str]] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateRender(BaseModel):
    """Render template with variables."""
    template_id: int
    variables: dict  # {"guest_name": "John", "check_in_date": "2026-01-15"}


# Conversation Schemas
class ConversationRead(BaseModel):
    """Conversation/thread response."""
    id: int
    thread_id: str
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    booking_id: Optional[int] = None
    primary_channel: MessageChannelEnum
    is_open: bool
    is_starred: bool
    assigned_to_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    message_count: int
    unread_count: int
    last_message_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Inbox Summary
class InboxSummary(BaseModel):
    """Unified inbox summary."""
    total_conversations: int
    open_conversations: int
    unread_messages: int
    starred: int
    by_channel: dict  # {"email": 10, "sms": 5}

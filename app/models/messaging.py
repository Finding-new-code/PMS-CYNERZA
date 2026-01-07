"""
Messaging models for unified inbox and communication with guests.
Supports email, SMS, and internal team messages.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class MessageChannel(str, enum.Enum):
    """Communication channel types."""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    INTERNAL = "internal"  # Team chat
    PUSH = "push"  # App push notification


class MessageDirection(str, enum.Enum):
    """Message direction."""
    INBOUND = "inbound"   # From guest
    OUTBOUND = "outbound"  # To guest


class MessageStatus(str, enum.Enum):
    """Message delivery status."""
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(Base):
    """
    Individual message in the unified inbox.
    Can be email, SMS, or internal message.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    
    # Channel and direction
    channel = Column(Enum(MessageChannel), nullable=False, index=True)
    direction = Column(Enum(MessageDirection), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.DRAFT, nullable=False)
    
    # Participants
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Contact info (for external messages)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(50), nullable=True)
    sender_email = Column(String(255), nullable=True)
    sender_phone = Column(String(50), nullable=True)
    
    # Content
    subject = Column(String(500), nullable=True)  # For emails
    body = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)  # HTML version for emails
    
    # Template reference
    template_id = Column(Integer, ForeignKey("message_templates.id"), nullable=True)
    
    # Threading
    thread_id = Column(String(100), nullable=True, index=True)  # Group related messages
    parent_id = Column(Integer, ForeignKey("messages.id"), nullable=True)  # Reply to
    
    # Read tracking
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    read_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    scheduled_at = Column(DateTime(timezone=True), nullable=True)  # For scheduled sends
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata
    external_id = Column(String(255), nullable=True)  # External service message ID
    metadata = Column(Text, nullable=True)  # JSON for additional data
    
    # Relationships
    booking = relationship("Booking")
    customer = relationship("Customer")
    sender_user = relationship("User", foreign_keys=[sender_user_id])
    read_by = relationship("User", foreign_keys=[read_by_id])
    template = relationship("MessageTemplate")
    parent = relationship("Message", remote_side=[id])

    def __repr__(self):
        return f"<Message {self.id} {self.channel.value} {self.direction.value}>"


class MessageTemplate(Base):
    """
    Reusable message templates with variable placeholders.
    Supports multiple languages for auto-translation.
    """
    __tablename__ = "message_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template info
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True, index=True)  # booking, welcome, review, etc.
    
    # Applicable channels
    channel = Column(Enum(MessageChannel), nullable=False)
    
    # Content
    subject = Column(String(500), nullable=True)  # For emails
    body = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)
    
    # Language
    language = Column(String(10), default="en", nullable=False)  # ISO code
    
    # Variables (JSON list of available placeholders)
    variables = Column(Text, nullable=True)  # ["guest_name", "check_in_date", ...]
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by = relationship("User")

    def __repr__(self):
        return f"<MessageTemplate {self.name} ({self.channel.value})>"


class Conversation(Base):
    """
    Conversation thread grouping multiple messages.
    Represents ongoing communication with a guest.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Participants
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    
    # Primary channel
    primary_channel = Column(Enum(MessageChannel), nullable=False)
    
    # Status
    is_open = Column(Boolean, default=True, nullable=False)
    is_starred = Column(Boolean, default=False, nullable=False)
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Stats
    message_count = Column(Integer, default=0)
    unread_count = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    booking = relationship("Booking")
    assigned_to = relationship("User")

    def __repr__(self):
        return f"<Conversation {self.thread_id}>"

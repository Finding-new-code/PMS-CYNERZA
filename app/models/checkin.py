"""
Digital Check-In models for online registration and document management.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class CheckInStatus(str, enum.Enum):
    """Digital check-in status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentType(str, enum.Enum):
    """Guest document types."""
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    VISA = "visa"
    CREDIT_CARD = "credit_card"
    OTHER = "other"


class DigitalCheckIn(Base):
    """
    Digital check-in record for a booking.
    Captures guest information, documents, and e-signature.
    """
    __tablename__ = "digital_checkins"

    id = Column(Integer, primary_key=True, index=True)
    
    # Booking reference
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    # Status
    status = Column(Enum(CheckInStatus), default=CheckInStatus.NOT_STARTED, nullable=False)
    
    # Personal information
    full_name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    nationality = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Arrival info
    estimated_arrival_time = Column(String(20), nullable=True)  # "14:00"
    special_requests = Column(Text, nullable=True)
    
    # E-signature
    signature_image = Column(Text, nullable=True)  # Base64 encoded
    signature_captured_at = Column(DateTime(timezone=True), nullable=True)
    signature_ip_address = Column(String(50), nullable=True)
    
    # Terms acceptance
    terms_accepted = Column(Boolean, default=False, nullable=False)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Verification
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # Unique access link
    access_token = Column(String(100), unique=True, nullable=True, index=True)
    link_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    booking = relationship("Booking")
    customer = relationship("Customer")
    verified_by = relationship("User")
    documents = relationship("GuestDocument", back_populates="checkin")

    def __repr__(self):
        return f"<DigitalCheckIn booking={self.booking_id} status={self.status.value}>"


class GuestDocument(Base):
    """
    Guest document uploads for verification.
    """
    __tablename__ = "guest_documents"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    checkin_id = Column(Integer, ForeignKey("digital_checkins.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    # Document info
    document_type = Column(Enum(DocumentType), nullable=False)
    document_number = Column(String(100), nullable=True)
    issuing_country = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # File storage
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)  # image/jpeg, application/pdf
    file_size = Column(Integer, nullable=True)  # bytes
    file_path = Column(String(500), nullable=True)  # Storage path or URL
    
    # Verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    checkin = relationship("DigitalCheckIn", back_populates="documents")
    customer = relationship("Customer")
    verified_by = relationship("User")

    def __repr__(self):
        return f"<GuestDocument {self.document_type.value} checkin={self.checkin_id}>"

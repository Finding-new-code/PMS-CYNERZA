"""
Pydantic schemas for Digital Check-In.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class CheckInStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentTypeEnum(str, Enum):
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    VISA = "visa"
    CREDIT_CARD = "credit_card"
    OTHER = "other"


# Digital Check-In Schemas
class CheckInStart(BaseModel):
    """Start digital check-in for a booking."""
    booking_id: int


class CheckInUpdate(BaseModel):
    """Update check-in information."""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    estimated_arrival_time: Optional[str] = None
    special_requests: Optional[str] = None


class SignatureCapture(BaseModel):
    """Capture e-signature."""
    signature_image: str  # Base64 encoded image
    terms_accepted: bool = True


class CheckInComplete(BaseModel):
    """Complete the check-in process."""
    signature_image: str
    terms_accepted: bool = True


class CheckInVerify(BaseModel):
    """Staff verification of check-in."""
    approve: bool
    notes: Optional[str] = None


class CheckInRead(BaseModel):
    """Digital check-in response."""
    id: int
    booking_id: int
    customer_id: Optional[int] = None
    status: CheckInStatusEnum
    
    # Personal info
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    
    # Arrival
    estimated_arrival_time: Optional[str] = None
    special_requests: Optional[str] = None
    
    # Signature
    has_signature: bool = False
    signature_captured_at: Optional[datetime] = None
    
    # Terms
    terms_accepted: bool
    terms_accepted_at: Optional[datetime] = None
    
    # Verification
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentUpload(BaseModel):
    """Upload a guest document."""
    checkin_id: int
    document_type: DocumentTypeEnum
    document_number: Optional[str] = None
    issuing_country: Optional[str] = None
    expiry_date: Optional[date] = None
    file_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None


class DocumentVerify(BaseModel):
    """Verify a guest document."""
    approve: bool
    rejection_reason: Optional[str] = None


class DocumentRead(BaseModel):
    """Guest document response."""
    id: int
    checkin_id: int
    document_type: DocumentTypeEnum
    document_number: Optional[str] = None
    issuing_country: Optional[str] = None
    expiry_date: Optional[date] = None
    file_name: str
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    is_verified: bool
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Check-In Link
class CheckInLink(BaseModel):
    """Digital check-in access link."""
    booking_id: int
    access_token: str
    link_url: str
    expires_at: datetime


# Summary
class CheckInSummary(BaseModel):
    """Digital check-in summary for dashboard."""
    total: int
    not_started: int
    in_progress: int
    completed: int
    verified: int
    pending_verification: int

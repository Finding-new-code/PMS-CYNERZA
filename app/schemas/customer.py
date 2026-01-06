"""
Pydantic schemas for customer management.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal


class CustomerBase(BaseModel):
    """Base customer schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    id_proof_type: Optional[str] = Field(None, max_length=50)
    id_proof_number: Optional[str] = Field(None, max_length=100)


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""
    is_vip: bool = False
    notes: Optional[str] = None
    preferences: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    id_proof_type: Optional[str] = Field(None, max_length=50)
    id_proof_number: Optional[str] = Field(None, max_length=100)
    is_vip: Optional[bool] = None
    vip_notes: Optional[str] = None
    notes: Optional[str] = None
    preferences: Optional[str] = None


class CustomerBookingSummary(BaseModel):
    """Brief booking info for customer response."""
    id: int
    room_type_name: str
    check_in: date
    check_out: date
    total_amount: Decimal
    amount_paid: Decimal
    status: str
    
    class Config:
        from_attributes = True


class CustomerRead(CustomerBase):
    """Schema for reading customer data with booking history."""
    id: int
    is_vip: bool = False
    vip_notes: Optional[str] = None
    lifetime_value: Decimal = Decimal("0.00")
    total_stays: int = 0
    notes: Optional[str] = None
    preferences: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_balance_due: Decimal = Decimal("0.00")
    bookings: List[CustomerBookingSummary] = []
    
    class Config:
        from_attributes = True


class CustomerListRead(CustomerBase):
    """Schema for customer list (without full booking details)."""
    id: int
    is_vip: bool = False
    lifetime_value: Decimal = Decimal("0.00")
    total_stays: int = 0
    created_at: datetime
    total_balance_due: Decimal = Decimal("0.00")
    booking_count: int = 0
    
    class Config:
        from_attributes = True


class GuestMergeRequest(BaseModel):
    """Schema for merging duplicate guest profiles."""
    primary_id: int = Field(..., gt=0, description="ID of the profile to keep")
    duplicate_ids: List[int] = Field(..., min_length=1, description="IDs of profiles to merge into primary")


class VIPStatusUpdate(BaseModel):
    """Schema for updating VIP status."""
    is_vip: bool
    vip_notes: Optional[str] = None


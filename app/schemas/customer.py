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
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    id_proof_type: Optional[str] = Field(None, max_length=50)
    id_proof_number: Optional[str] = Field(None, max_length=100)


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
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_balance_due: Decimal = Decimal("0.00")
    bookings: List[CustomerBookingSummary] = []
    
    class Config:
        from_attributes = True


class CustomerListRead(CustomerBase):
    """Schema for customer list (without full booking details)."""
    id: int
    created_at: datetime
    total_balance_due: Decimal = Decimal("0.00")
    booking_count: int = 0
    
    class Config:
        from_attributes = True

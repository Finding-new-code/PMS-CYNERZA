"""
Pydantic schemas for Upsell Store.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class ProductCategoryEnum(str, Enum):
    ROOM_UPGRADE = "room_upgrade"
    EARLY_CHECKIN = "early_checkin"
    LATE_CHECKOUT = "late_checkout"
    BREAKFAST = "breakfast"
    SPA = "spa"
    TRANSPORT = "transport"
    EXPERIENCE = "experience"
    AMENITY = "amenity"
    OTHER = "other"


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


# Product Schemas
class ProductCreate(BaseModel):
    """Create a new upsell product."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: ProductCategoryEnum
    price: Decimal
    tax_rate: Decimal = Decimal("0")
    image_url: Optional[str] = None
    display_order: int = 0
    available_in_booking: bool = True
    available_in_stay: bool = True
    has_inventory: bool = False
    inventory_count: int = 0
    lead_time_hours: int = 0


class ProductUpdate(BaseModel):
    """Update a product."""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProductCategoryEnum] = None
    price: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    available_in_booking: Optional[bool] = None
    available_in_stay: Optional[bool] = None
    has_inventory: Optional[bool] = None
    inventory_count: Optional[int] = None


class ProductRead(BaseModel):
    """Product response."""
    id: int
    name: str
    description: Optional[str] = None
    category: ProductCategoryEnum
    price: Decimal
    tax_rate: Decimal
    image_url: Optional[str] = None
    display_order: int
    is_active: bool
    available_in_booking: bool
    available_in_stay: bool
    has_inventory: bool
    inventory_count: int
    lead_time_hours: int
    created_at: datetime

    class Config:
        from_attributes = True


# Order Item Schemas
class OrderItemCreate(BaseModel):
    """Add item to order."""
    product_id: int
    quantity: int = 1
    notes: Optional[str] = None


class OrderItemRead(BaseModel):
    """Order item response."""
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    unit_price: Decimal
    tax_amount: Decimal
    total_price: Decimal
    notes: Optional[str] = None
    is_fulfilled: bool
    is_posted_to_folio: bool

    class Config:
        from_attributes = True


# Order Schemas
class OrderCreate(BaseModel):
    """Create an upsell order."""
    booking_id: int
    items: List[OrderItemCreate]
    requested_date: Optional[datetime] = None
    guest_notes: Optional[str] = None


class OrderUpdate(BaseModel):
    """Update order status."""
    status: Optional[OrderStatusEnum] = None
    staff_notes: Optional[str] = None
    requested_date: Optional[datetime] = None


class OrderRead(BaseModel):
    """Order response."""
    id: int
    booking_id: int
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    status: OrderStatusEnum
    requested_date: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    guest_notes: Optional[str] = None
    staff_notes: Optional[str] = None
    items: List[OrderItemRead] = []
    total_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class OrderFulfill(BaseModel):
    """Fulfill an order."""
    notes: Optional[str] = None


# Summary
class UpsellSummary(BaseModel):
    """Upsell dashboard summary."""
    total_products: int
    active_products: int
    pending_orders: int
    fulfilled_today: int
    revenue_today: Decimal
    top_products: List[dict]

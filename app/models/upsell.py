"""
Upsell Store models for product catalog and order management.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ProductCategory(str, enum.Enum):
    """Product categories for upsell."""
    ROOM_UPGRADE = "room_upgrade"
    EARLY_CHECKIN = "early_checkin"
    LATE_CHECKOUT = "late_checkout"
    BREAKFAST = "breakfast"
    SPA = "spa"
    TRANSPORT = "transport"
    EXPERIENCE = "experience"
    AMENITY = "amenity"
    OTHER = "other"


class OrderStatus(str, enum.Enum):
    """Upsell order status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class UpsellProduct(Base):
    """
    Product in the upsell catalog.
    """
    __tablename__ = "upsell_products"

    id = Column(Integer, primary_key=True, index=True)
    
    # Product info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 4), default=0)  # 0.10 = 10%
    
    # Display
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0)
    
    # Availability
    is_active = Column(Boolean, default=True, nullable=False)
    available_in_booking = Column(Boolean, default=True)  # During booking flow
    available_in_stay = Column(Boolean, default=True)  # During stay
    
    # Inventory (optional)
    has_inventory = Column(Boolean, default=False)
    inventory_count = Column(Integer, default=0)
    
    # Timing
    lead_time_hours = Column(Integer, default=0)  # Hours before can be fulfilled
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<UpsellProduct {self.name} ({self.category.value})>"


class UpsellOrder(Base):
    """
    Guest order for upsell products.
    """
    __tablename__ = "upsell_orders"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Timing
    requested_date = Column(DateTime, nullable=True)  # When service is requested
    fulfilled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    guest_notes = Column(Text, nullable=True)
    staff_notes = Column(Text, nullable=True)
    
    # Staff handling
    fulfilled_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    booking = relationship("Booking")
    customer = relationship("Customer")
    fulfilled_by = relationship("User")
    items = relationship("UpsellOrderItem", back_populates="order")

    def __repr__(self):
        return f"<UpsellOrder {self.id} booking={self.booking_id}>"


class UpsellOrderItem(Base):
    """
    Line item in an upsell order.
    """
    __tablename__ = "upsell_order_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    order_id = Column(Integer, ForeignKey("upsell_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("upsell_products.id"), nullable=False)
    
    # Pricing at time of order
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Status (for individual item tracking)
    is_fulfilled = Column(Boolean, default=False, nullable=False)
    
    # Folio posting
    is_posted_to_folio = Column(Boolean, default=False, nullable=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    order = relationship("UpsellOrder", back_populates="items")
    product = relationship("UpsellProduct")

    def __repr__(self):
        return f"<UpsellOrderItem {self.product_id} qty={self.quantity}>"

"""
Upsell Store service for product catalog and order management.
"""

from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.upsell import UpsellProduct, UpsellOrder, UpsellOrderItem, ProductCategory, OrderStatus
from app.models.booking import Booking


async def create_product(db: AsyncSession, product_data: dict) -> UpsellProduct:
    """Create a new upsell product."""
    product = UpsellProduct(**product_data)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def get_products(
    db: AsyncSession,
    category: Optional[ProductCategory] = None,
    active_only: bool = True,
    in_booking: Optional[bool] = None,
    in_stay: Optional[bool] = None
) -> List[UpsellProduct]:
    """Get products with filters."""
    query = select(UpsellProduct)
    
    if category:
        query = query.where(UpsellProduct.category == category)
    if active_only:
        query = query.where(UpsellProduct.is_active == True)
    if in_booking is not None:
        query = query.where(UpsellProduct.available_in_booking == in_booking)
    if in_stay is not None:
        query = query.where(UpsellProduct.available_in_stay == in_stay)
    
    query = query.order_by(UpsellProduct.display_order, UpsellProduct.name)
    result = await db.execute(query)
    return result.scalars().all()


async def update_product(
    db: AsyncSession,
    product_id: int,
    updates: dict
) -> Optional[UpsellProduct]:
    """Update a product."""
    query = select(UpsellProduct).where(UpsellProduct.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        return None
    
    for key, value in updates.items():
        if value is not None and hasattr(product, key):
            setattr(product, key, value)
    
    await db.commit()
    await db.refresh(product)
    return product


async def create_order(
    db: AsyncSession,
    booking_id: int,
    items: List[dict],
    requested_date: Optional[datetime] = None,
    guest_notes: Optional[str] = None
) -> UpsellOrder:
    """Create an upsell order with items."""
    # Get booking for customer_id
    booking_query = select(Booking).where(Booking.id == booking_id)
    booking = (await db.execute(booking_query)).scalar_one_or_none()
    
    if not booking:
        raise ValueError("Booking not found")
    
    order = UpsellOrder(
        booking_id=booking_id,
        customer_id=booking.customer_id,
        status=OrderStatus.PENDING,
        requested_date=requested_date,
        guest_notes=guest_notes
    )
    db.add(order)
    await db.flush()
    
    # Add items
    for item_data in items:
        product_query = select(UpsellProduct).where(
            UpsellProduct.id == item_data["product_id"]
        )
        product = (await db.execute(product_query)).scalar_one_or_none()
        
        if not product:
            continue
        
        quantity = item_data.get("quantity", 1)
        unit_price = product.price
        tax_amount = unit_price * product.tax_rate * quantity
        total_price = (unit_price * quantity) + tax_amount
        
        order_item = UpsellOrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            tax_amount=tax_amount,
            total_price=total_price,
            notes=item_data.get("notes")
        )
        db.add(order_item)
        
        # Update inventory if applicable
        if product.has_inventory and product.inventory_count >= quantity:
            product.inventory_count -= quantity
    
    await db.commit()
    await db.refresh(order)
    return order


async def get_orders(
    db: AsyncSession,
    booking_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    limit: int = 50,
    offset: int = 0
) -> List[UpsellOrder]:
    """Get orders with filters."""
    query = select(UpsellOrder).options(
        selectinload(UpsellOrder.items).selectinload(UpsellOrderItem.product),
        selectinload(UpsellOrder.customer)
    )
    
    if booking_id:
        query = query.where(UpsellOrder.booking_id == booking_id)
    if status:
        query = query.where(UpsellOrder.status == status)
    
    query = query.order_by(UpsellOrder.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def fulfill_order(
    db: AsyncSession,
    order_id: int,
    user_id: int,
    notes: Optional[str] = None
) -> UpsellOrder:
    """Mark order as fulfilled."""
    query = select(UpsellOrder).options(
        selectinload(UpsellOrder.items)
    ).where(UpsellOrder.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise ValueError("Order not found")
    
    order.status = OrderStatus.FULFILLED
    order.fulfilled_at = datetime.utcnow()
    order.fulfilled_by_id = user_id
    
    if notes:
        order.staff_notes = notes
    
    # Mark all items as fulfilled
    for item in order.items:
        item.is_fulfilled = True
    
    await db.commit()
    await db.refresh(order)
    return order


async def get_upsell_summary(db: AsyncSession) -> dict:
    """Get upsell dashboard summary."""
    # Total products
    total_query = select(func.count(UpsellProduct.id))
    total = (await db.execute(total_query)).scalar() or 0
    
    # Active products
    active_query = select(func.count(UpsellProduct.id)).where(
        UpsellProduct.is_active == True
    )
    active = (await db.execute(active_query)).scalar() or 0
    
    # Pending orders
    pending_query = select(func.count(UpsellOrder.id)).where(
        UpsellOrder.status == OrderStatus.PENDING
    )
    pending = (await db.execute(pending_query)).scalar() or 0
    
    # Fulfilled today
    today_start = datetime.combine(date.today(), datetime.min.time())
    fulfilled_query = select(func.count(UpsellOrder.id)).where(
        and_(
            UpsellOrder.status == OrderStatus.FULFILLED,
            UpsellOrder.fulfilled_at >= today_start
        )
    )
    fulfilled_today = (await db.execute(fulfilled_query)).scalar() or 0
    
    # Revenue today
    revenue_query = select(func.sum(UpsellOrderItem.total_price)).join(
        UpsellOrder
    ).where(
        and_(
            UpsellOrder.status == OrderStatus.FULFILLED,
            UpsellOrder.fulfilled_at >= today_start
        )
    )
    revenue = (await db.execute(revenue_query)).scalar() or Decimal("0")
    
    # Top products (by order count)
    top_query = select(
        UpsellProduct.name,
        func.count(UpsellOrderItem.id).label("order_count")
    ).join(UpsellOrderItem).group_by(
        UpsellProduct.id
    ).order_by(func.count(UpsellOrderItem.id).desc()).limit(5)
    
    top_result = await db.execute(top_query)
    top_products = [{"name": row[0], "orders": row[1]} for row in top_result]
    
    return {
        "total_products": total,
        "active_products": active,
        "pending_orders": pending,
        "fulfilled_today": fulfilled_today,
        "revenue_today": revenue,
        "top_products": top_products
    }

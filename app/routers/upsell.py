"""
Upsell Store API router for product catalog and order management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.upsell import (
    ProductCreate, ProductUpdate, ProductRead,
    OrderCreate, OrderUpdate, OrderRead, OrderFulfill, OrderItemRead,
    UpsellSummary, ProductCategoryEnum, OrderStatusEnum
)
from app.services import upsell_service
from app.models.upsell import ProductCategory, OrderStatus

router = APIRouter(prefix="/upsell", tags=["Upsell Store"])


# ============ Products ============

@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new upsell product."""
    data = product_data.model_dump()
    data["category"] = ProductCategory(product_data.category.value)
    
    product = await upsell_service.create_product(db, data)
    
    return ProductRead(
        id=product.id,
        name=product.name,
        description=product.description,
        category=ProductCategoryEnum(product.category.value),
        price=product.price,
        tax_rate=product.tax_rate,
        image_url=product.image_url,
        display_order=product.display_order,
        is_active=product.is_active,
        available_in_booking=product.available_in_booking,
        available_in_stay=product.available_in_stay,
        has_inventory=product.has_inventory,
        inventory_count=product.inventory_count,
        lead_time_hours=product.lead_time_hours,
        created_at=product.created_at
    )


@router.get("/products", response_model=List[ProductRead])
async def list_products(
    category: Optional[ProductCategoryEnum] = Query(None),
    active_only: bool = Query(True),
    in_booking: Optional[bool] = Query(None),
    in_stay: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get upsell products (no auth required for guest access)."""
    cat_filter = ProductCategory(category.value) if category else None
    
    products = await upsell_service.get_products(
        db, cat_filter, active_only, in_booking, in_stay
    )
    
    return [
        ProductRead(
            id=p.id,
            name=p.name,
            description=p.description,
            category=ProductCategoryEnum(p.category.value),
            price=p.price,
            tax_rate=p.tax_rate,
            image_url=p.image_url,
            display_order=p.display_order,
            is_active=p.is_active,
            available_in_booking=p.available_in_booking,
            available_in_stay=p.available_in_stay,
            has_inventory=p.has_inventory,
            inventory_count=p.inventory_count,
            lead_time_hours=p.lead_time_hours,
            created_at=p.created_at
        )
        for p in products
    ]


@router.patch("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    updates: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product."""
    update_data = updates.model_dump(exclude_unset=True)
    
    if "category" in update_data and update_data["category"]:
        update_data["category"] = ProductCategory(update_data["category"].value)
    
    product = await upsell_service.update_product(db, product_id, update_data)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductRead(
        id=product.id,
        name=product.name,
        description=product.description,
        category=ProductCategoryEnum(product.category.value),
        price=product.price,
        tax_rate=product.tax_rate,
        image_url=product.image_url,
        display_order=product.display_order,
        is_active=product.is_active,
        available_in_booking=product.available_in_booking,
        available_in_stay=product.available_in_stay,
        has_inventory=product.has_inventory,
        inventory_count=product.inventory_count,
        lead_time_hours=product.lead_time_hours,
        created_at=product.created_at
    )


# ============ Orders ============

@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create an upsell order (guest-facing, no auth)."""
    try:
        items = [item.model_dump() for item in order_data.items]
        
        order = await upsell_service.create_order(
            db, order_data.booking_id, items,
            order_data.requested_date, order_data.guest_notes
        )
        
        # Calculate total
        total = sum(item.total_price for item in order.items) if order.items else Decimal("0")
        
        return OrderRead(
            id=order.id,
            booking_id=order.booking_id,
            customer_id=order.customer_id,
            customer_name=order.customer.name if order.customer else None,
            status=OrderStatusEnum(order.status.value),
            requested_date=order.requested_date,
            fulfilled_at=order.fulfilled_at,
            guest_notes=order.guest_notes,
            staff_notes=order.staff_notes,
            items=[
                OrderItemRead(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product.name if item.product else None,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_amount=item.tax_amount,
                    total_price=item.total_price,
                    notes=item.notes,
                    is_fulfilled=item.is_fulfilled,
                    is_posted_to_folio=item.is_posted_to_folio
                )
                for item in order.items
            ],
            total_amount=total,
            created_at=order.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/orders", response_model=List[OrderRead])
async def list_orders(
    booking_id: Optional[int] = Query(None),
    status: Optional[OrderStatusEnum] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upsell orders."""
    status_filter = OrderStatus(status.value) if status else None
    
    orders = await upsell_service.get_orders(
        db, booking_id, status_filter, limit, offset
    )
    
    result = []
    for order in orders:
        total = sum(item.total_price for item in order.items) if order.items else Decimal("0")
        
        result.append(OrderRead(
            id=order.id,
            booking_id=order.booking_id,
            customer_id=order.customer_id,
            customer_name=order.customer.name if order.customer else None,
            status=OrderStatusEnum(order.status.value),
            requested_date=order.requested_date,
            fulfilled_at=order.fulfilled_at,
            guest_notes=order.guest_notes,
            staff_notes=order.staff_notes,
            items=[
                OrderItemRead(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product.name if item.product else None,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_amount=item.tax_amount,
                    total_price=item.total_price,
                    notes=item.notes,
                    is_fulfilled=item.is_fulfilled,
                    is_posted_to_folio=item.is_posted_to_folio
                )
                for item in order.items
            ],
            total_amount=total,
            created_at=order.created_at
        ))
    
    return result


@router.post("/orders/{order_id}/fulfill")
async def fulfill_order(
    order_id: int,
    fulfill_data: OrderFulfill,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark order as fulfilled."""
    try:
        order = await upsell_service.fulfill_order(
            db, order_id, current_user.id, fulfill_data.notes
        )
        return {
            "message": "Order fulfilled",
            "status": order.status.value,
            "fulfilled_at": order.fulfilled_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============ Summary ============

@router.get("/summary", response_model=UpsellSummary)
async def get_upsell_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upsell dashboard summary."""
    summary = await upsell_service.get_upsell_summary(db)
    return UpsellSummary(**summary)

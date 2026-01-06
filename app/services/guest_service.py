"""
Guest service for customer profile management.
Handles VIP status, merge/deduplication, and notes.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from decimal import Decimal

from app.models.customer import Customer
from app.models.booking import Booking


async def merge_guests(
    db: AsyncSession,
    primary_id: int,
    duplicate_ids: List[int],
) -> Optional[Customer]:
    """
    Merge duplicate guest profiles into a primary profile.
    All bookings from duplicate profiles are transferred to the primary.
    Duplicate profiles are deleted after merge.
    """
    # Get primary customer
    result = await db.execute(
        select(Customer).where(Customer.id == primary_id)
    )
    primary = result.scalar_one_or_none()
    if not primary:
        return None
    
    # Get duplicates
    for dup_id in duplicate_ids:
        if dup_id == primary_id:
            continue
        
        dup_result = await db.execute(
            select(Customer).where(Customer.id == dup_id)
        )
        duplicate = dup_result.scalar_one_or_none()
        
        if not duplicate:
            continue
        
        # Transfer bookings to primary
        await db.execute(
            Booking.__table__.update()
            .where(Booking.customer_id == dup_id)
            .values(customer_id=primary_id)
        )
        
        # Merge stats
        primary.lifetime_value = Decimal(primary.lifetime_value or 0) + Decimal(duplicate.lifetime_value or 0)
        primary.total_stays = (primary.total_stays or 0) + (duplicate.total_stays or 0)
        
        # Merge notes (append)
        if duplicate.notes:
            if primary.notes:
                primary.notes = f"{primary.notes}\n\n[Merged from {duplicate.email}]:\n{duplicate.notes}"
            else:
                primary.notes = f"[Merged from {duplicate.email}]:\n{duplicate.notes}"
        
        # Copy missing data
        if not primary.phone and duplicate.phone:
            primary.phone = duplicate.phone
        if not primary.address and duplicate.address:
            primary.address = duplicate.address
        if not primary.id_proof_type and duplicate.id_proof_type:
            primary.id_proof_type = duplicate.id_proof_type
            primary.id_proof_number = duplicate.id_proof_number
        if not primary.preferences and duplicate.preferences:
            primary.preferences = duplicate.preferences
        
        # Delete duplicate
        await db.delete(duplicate)
    
    await db.commit()
    await db.refresh(primary)
    return primary


async def find_potential_duplicates(
    db: AsyncSession,
    customer_id: int,
) -> List[Customer]:
    """
    Find potential duplicate profiles for a customer.
    Matches by similar name, email prefix, or phone.
    """
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        return []
    
    # Build search conditions
    conditions = []
    
    # Similar name (case-insensitive)
    name_parts = customer.name.split()
    for part in name_parts:
        if len(part) > 2:
            conditions.append(Customer.name.ilike(f"%{part}%"))
    
    # Same phone
    if customer.phone:
        conditions.append(Customer.phone == customer.phone)
    
    # Similar email (same domain or prefix)
    if customer.email:
        email_parts = customer.email.split("@")
        if len(email_parts) == 2:
            conditions.append(Customer.email.ilike(f"%@{email_parts[1]}"))
    
    if not conditions:
        return []
    
    # Find potential matches (exclude self)
    result = await db.execute(
        select(Customer).where(
            Customer.id != customer_id,
            or_(*conditions)
        ).limit(10)
    )
    return list(result.scalars().all())


async def update_vip_status(
    db: AsyncSession,
    customer_id: int,
    is_vip: bool,
    vip_notes: Optional[str] = None,
) -> Optional[Customer]:
    """
    Update VIP status for a customer.
    """
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        return None
    
    customer.is_vip = is_vip
    if vip_notes is not None:
        customer.vip_notes = vip_notes
    
    await db.commit()
    await db.refresh(customer)
    return customer


async def recalculate_lifetime_value(
    db: AsyncSession,
    customer_id: int,
) -> Optional[Customer]:
    """
    Recalculate lifetime value and total stays from booking history.
    """
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        return None
    
    # Calculate from bookings
    stats_result = await db.execute(
        select(
            func.sum(Booking.total_amount).label("total_spent"),
            func.count(Booking.id).label("stay_count")
        ).where(
            Booking.customer_id == customer_id,
            Booking.status.in_(["confirmed", "checked_in", "checked_out"])
        )
    )
    stats = stats_result.one()
    
    customer.lifetime_value = stats.total_spent or Decimal(0)
    customer.total_stays = stats.stay_count or 0
    
    await db.commit()
    await db.refresh(customer)
    return customer

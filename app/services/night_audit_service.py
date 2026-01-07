"""
Night Audit service for daily audit processing, rate posting, and no-show handling.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple
from decimal import Decimal
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.night_audit import NightAudit, RoomCharge
from app.models.booking import Booking, BookingStatus
from app.models.room import Room, OccupancyStatus
from app.models.room_type import RoomType


async def get_latest_audit(db: AsyncSession) -> Optional[NightAudit]:
    """Get the most recent night audit."""
    query = select(NightAudit).order_by(NightAudit.business_date.desc()).limit(1)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_audit_by_date(db: AsyncSession, business_date: date) -> Optional[NightAudit]:
    """Get night audit for a specific date."""
    query = select(NightAudit).where(NightAudit.business_date == business_date)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def run_night_audit(
    db: AsyncSession,
    business_date: date,
    user_id: Optional[int] = None
) -> NightAudit:
    """
    Run the complete night audit process.
    Steps:
    1. Create audit record
    2. Process no-shows
    3. Post room charges for occupied rooms
    4. Calculate statistics
    5. Mark audit as complete
    """
    # Check if audit already run for this date
    existing = await get_audit_by_date(db, business_date)
    if existing and existing.is_completed:
        raise ValueError(f"Night audit already completed for {business_date}")
    
    # Create or get audit record
    if existing:
        audit = existing
    else:
        audit = NightAudit(
            business_date=business_date,
            started_at=datetime.utcnow(),
            run_by_id=user_id
        )
        db.add(audit)
        await db.flush()
    
    # Step 1: Process no-shows
    no_shows, no_show_revenue = await process_no_shows(db, business_date)
    audit.no_shows_processed = len(no_shows)
    audit.no_show_revenue_lost = no_show_revenue
    
    # Step 2: Post room charges for occupied rooms
    charges_posted = await post_room_charges(db, audit.id, business_date)
    audit.room_charges_posted = len(charges_posted)
    
    # Step 3: Calculate revenue totals
    room_revenue = sum(charge.total_charge for charge in charges_posted)
    tax_total = sum(charge.tax_amount for charge in charges_posted)
    audit.total_room_revenue = room_revenue
    audit.total_tax = tax_total
    
    # Step 4: Calculate occupancy statistics
    stats = await calculate_occupancy_stats(db, business_date)
    audit.rooms_occupied = stats["occupied"]
    audit.rooms_available = stats["available"]
    audit.rooms_out_of_service = stats["out_of_service"]
    audit.occupancy_percentage = stats["occupancy_pct"]
    
    # Mark as complete
    audit.is_completed = True
    audit.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(audit)
    
    return audit


async def process_no_shows(
    db: AsyncSession,
    business_date: date
) -> Tuple[List[Booking], Decimal]:
    """
    Process no-show bookings for the given business date.
    Returns list of no-show bookings and total revenue lost.
    """
    # Find bookings with check-in on business_date that are still pending
    query = select(Booking).where(
        and_(
            Booking.check_in == business_date,
            Booking.status == BookingStatus.PENDING
        )
    )
    result = await db.execute(query)
    pending_arrivals = result.scalars().all()
    
    no_shows = []
    total_revenue_lost = Decimal("0.00")
    
    # Mark as no-show if past a certain time (e.g., midnight of next day)
    for booking in pending_arrivals:
        # Cancel the booking and mark as no-show
        booking.status = BookingStatus.NO_SHOW
        booking.notes = (booking.notes or "") + f"\nMarked as no-show by night audit on {datetime.utcnow().date()}"
        
        no_shows.append(booking)
        # Calculate revenue lost (could charge partial or full rate)
        # For now, we'll track the full booking amount as lost revenue
        total_revenue_lost += booking.balance_due
    
    await db.flush()
    
    return no_shows, total_revenue_lost


async def post_room_charges(
    db: AsyncSession,
    audit_id: int,
    business_date: date
) -> List[RoomCharge]:
    """
    Post room charges for all occupied rooms on the business date.
    Creates RoomCharge records for each occupied room.
    """
    # Find all active bookings that overlap with business_date
    query = select(Booking).options(
        selectinload(Booking.room_type)
    ).where(
        and_(
            Booking.check_in <= business_date,
            Booking.check_out > business_date,
            Booking.status == BookingStatus.CONFIRMED
        )
    )
    result = await db.execute(query)
    active_bookings = result.scalars().all()
    
    charges = []
    
    for booking in active_bookings:
        # Calculate daily rate
        total_days = (booking.check_out - booking.check_in).days
        if total_days == 0:
            total_days = 1
        
        daily_rate = booking.total_amount / Decimal(str(total_days))
        
        # For simplicity, assume 10% tax (in production, use proper tax engine)
        tax_amount = daily_rate * Decimal("0.10")
        total_charge = daily_rate + tax_amount
        
        # Create room charge record
        charge = RoomCharge(
            night_audit_id=audit_id,
            booking_id=booking.id,
            room_number=None,  # TODO: Link to actual room assignment
            business_date=business_date,
            room_rate=daily_rate,
            tax_amount=tax_amount,
            total_charge=total_charge,
            is_posted=True
        )
        db.add(charge)
        charges.append(charge)
    
    await db.flush()
    
    return charges


async def calculate_occupancy_stats(
    db: AsyncSession,
    business_date: date
) -> dict:
    """
    Calculate occupancy statistics for the business date.
    """
    # Get total rooms from room types
    total_rooms_query = select(func.sum(RoomType.total_rooms))
    result = await db.execute(total_rooms_query)
    total_rooms = result.scalar() or 0
    
    # Count occupied rooms (active bookings on this date)
    occupied_query = select(func.count(Booking.id)).where(
        and_(
            Booking.check_in <= business_date,
            Booking.check_out > business_date,
            Booking.status == BookingStatus.CONFIRMED
        )
    )
    result = await db.execute(occupied_query)
    occupied = result.scalar() or 0
    
    # Count out of service rooms (if Room table exists)
    out_of_service = 0
    try:
        oos_query = select(func.count(Room.id)).where(
            Room.housekeeping_status.in_(["out_of_order", "out_of_service"])
        )
        result = await db.execute(oos_query)
        out_of_service = result.scalar() or 0
    except:
        pass  # Room table may not have data yet
    
    available = total_rooms - occupied - out_of_service
    
    occupancy_pct = Decimal("0.00")
    if total_rooms > 0:
        occupancy_pct = Decimal(str(occupied)) / Decimal(str(total_rooms)) * Decimal("100")
    
    return {
        "total_rooms": total_rooms,
        "occupied": occupied,
        "available": available,
        "out_of_service": out_of_service,
        "occupancy_pct": round(occupancy_pct, 2)
    }


async def generate_reconciliation_report(
    db: AsyncSession,
    business_date: date
) -> dict:
    """
    Generate a reconciliation report for the given business date.
    """
    audit = await get_audit_by_date(db, business_date)
    
    if not audit:
        raise ValueError(f"No audit found for {business_date}")
    
    # Calculate ADR and RevPAR
    adr = Decimal("0.00")
    revpar = Decimal("0.00")
    
    if audit.rooms_occupied > 0:
        adr = audit.total_room_revenue / Decimal(str(audit.rooms_occupied))
    
    total_rooms = audit.rooms_occupied + audit.rooms_available + audit.rooms_out_of_service
    if total_rooms > 0:
        revpar = audit.total_room_revenue / Decimal(str(total_rooms))
    
    # Get arrival/departure counts
    arrivals_query = select(func.count(Booking.id)).where(
        Booking.check_in == business_date
    )
    arrivals_result = await db.execute(arrivals_query)
    arrivals = arrivals_result.scalar() or 0
    
    departures_query = select(func.count(Booking.id)).where(
        Booking.check_out == business_date
    )
    departures_result = await db.execute(departures_query)
    departures = departures_result.scalar() or 0
    
    stayovers = audit.rooms_occupied - arrivals
    
    return {
        "business_date": business_date,
        "room_revenue": audit.total_room_revenue,
        "other_revenue": audit.total_other_revenue,
        "total_revenue": audit.total_room_revenue + audit.total_other_revenue,
        "total_tax": audit.total_tax,
        "gross_total": audit.total_room_revenue + audit.total_other_revenue + audit.total_tax,
        "total_payments": audit.total_payments,
        "outstanding_balance": Decimal("0.00"),  # TODO: Calculate from bookings
        "rooms_occupied": audit.rooms_occupied,
        "rooms_available": audit.rooms_available,
        "rooms_out_of_service": audit.rooms_out_of_service,
        "occupancy_rate": audit.occupancy_percentage,
        "average_daily_rate": round(adr, 2),
        "revenue_per_available_room": round(revpar, 2),
        "arrivals": arrivals,
        "departures": departures,
        "stayovers": stayovers,
        "no_shows": audit.no_shows_processed,
        "room_charges_posted": audit.room_charges_posted,
        "no_show_charges": 0  # TODO: Track separately
    }


async def list_audits(
    db: AsyncSession,
    limit: int = 30,
    offset: int = 0
) -> List[NightAudit]:
    """List night audits with pagination."""
    query = select(NightAudit).order_by(
        NightAudit.business_date.desc()
    ).offset(offset).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

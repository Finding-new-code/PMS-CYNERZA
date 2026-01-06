"""
Dashboard service - provides real-time operational metrics and forecasting.
All calculations are optimized for dashboard performance.
"""

from datetime import date, timedelta, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case

from app.models.booking import Booking, BookingStatus
from app.models.inventory import Inventory
from app.models.room_type import RoomType


async def get_todays_activity(db: AsyncSession) -> dict:
    """
    Get real-time operational metrics for today.
    
    Returns:
        Dictionary with arrivals, departures, in-house guests, and issues
    """
    today = date.today()
    
    # --- Arrivals ---
    # Expected arrivals: bookings with check_in = today
    arrivals_result = await db.execute(
        select(
            func.count(Booking.id).label('total'),
            func.sum(case((Booking.status == BookingStatus.CHECKED_IN.value, 1), else_=0)).label('checked_in')
        ).where(
            and_(
                Booking.check_in == today,
                Booking.status.in_([
                    BookingStatus.CONFIRMED.value,
                    BookingStatus.CHECKED_IN.value
                ])
            )
        )
    )
    arrivals = arrivals_result.one()
    arrivals_expected = arrivals.total or 0
    arrivals_checked_in = arrivals.checked_in or 0
    arrivals_pending = arrivals_expected - arrivals_checked_in
    
    # --- Departures ---
    # Expected departures: bookings with check_out = today
    departures_result = await db.execute(
        select(
            func.count(Booking.id).label('total'),
            func.sum(case((Booking.status == BookingStatus.CHECKED_OUT.value, 1), else_=0)).label('checked_out')
        ).where(
            and_(
                Booking.check_out == today,
                Booking.status.in_([
                    BookingStatus.CHECKED_IN.value,
                    BookingStatus.CHECKED_OUT.value
                ])
            )
        )
    )
    departures = departures_result.one()
    departures_expected = departures.total or 0
    departures_checked_out = departures.checked_out or 0
    departures_pending = departures_expected - departures_checked_out
    
    # --- In-House Guests ---
    # Guests currently staying: checked_in and not checked_out
    inhouse_result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.status == BookingStatus.CHECKED_IN.value
        )
    )
    in_house_guests = inhouse_result.scalar() or 0
    
    # --- Issues ---
    # Overbookings: Check if any room type has negative availability for today
    # Join inventory with room_type to compare available vs total
    overbooking_result = await db.execute(
        select(func.count()).select_from(Inventory).join(
            RoomType, Inventory.room_type_id == RoomType.id
        ).where(
            and_(
                Inventory.date == today,
                Inventory.available_rooms < 0
            )
        )
    )
    overbookings = overbooking_result.scalar() or 0
    
    # Cancellations today (by updated_at date)
    cancellations_result = await db.execute(
        select(func.count(Booking.id)).where(
            and_(
                Booking.status == BookingStatus.CANCELLED.value,
                func.date(Booking.updated_at) == today
            )
        )
    )
    cancellations_today = cancellations_result.scalar() or 0
    
    # No-shows: simplified for now
    no_shows = 0
    
    return {
        "arrivals_expected": arrivals_expected,
        "arrivals_checked_in": arrivals_checked_in,
        "arrivals_pending": arrivals_pending,
        "departures_expected": departures_expected,
        "departures_checked_out": departures_checked_out,
        "departures_pending": departures_pending,
        "in_house_guests": in_house_guests,
        "overbookings": overbookings,
        "cancellations_today": cancellations_today,
        "no_shows": no_shows
    }


async def get_14day_forecast(db: AsyncSession) -> dict:
    """
    Generate 14-day forward forecast for occupancy and revenue.
    
    Returns:
        Dictionary with daily forecast data and summary metrics
    """
    today = date.today()
    end_date = today + timedelta(days=14)
    
    # Get inventory joined with room_type for next 14 days
    inventory_result = await db.execute(
        select(
            Inventory.date,
            Inventory.room_type_id,
            Inventory.available_rooms,
            RoomType.total_rooms
        ).join(
            RoomType, Inventory.room_type_id == RoomType.id
        ).where(
            and_(
                Inventory.date >= today,
                Inventory.date < end_date
            )
        ).order_by(Inventory.date)
    )
    
    # Get bookings for arrivals/departures count
    bookings_result = await db.execute(
        select(
            Booking.check_in,
            Booking.check_out,
            Booking.total_amount,
            Booking.num_rooms
        ).where(
            and_(
                or_(
                    and_(Booking.check_in >= today, Booking.check_in < end_date),
                    and_(Booking.check_out >= today, Booking.check_out < end_date)
                ),
                Booking.status == BookingStatus.CONFIRMED.value
            )
        )
    )
    
    # Aggregate inventory by date
    inventory_by_date = {}
    for row in inventory_result:
        if row.date not in inventory_by_date:
            inventory_by_date[row.date] = {
                "available": 0,
                "total": 0
            }
        inventory_by_date[row.date]["available"] += row.available_rooms
        inventory_by_date[row.date]["total"] += row.total_rooms
    
    # Count arrivals and departures by date
    arrivals_by_date = {}
    departures_by_date = {}
    revenue_by_date = {}
    
    for row in bookings_result:
        # Arrivals
        if today <= row.check_in < end_date:
            arrivals_by_date[row.check_in] = arrivals_by_date.get(row.check_in, 0) + 1
        
        # Departures
        if today <= row.check_out < end_date:
            departures_by_date[row.check_out] = departures_by_date.get(row.check_out, 0) + 1
        
        # Revenue (simplified - attribute to check-in date)
        if today <= row.check_in < end_date:
            revenue_by_date[row.check_in] = revenue_by_date.get(row.check_in, Decimal(0)) + Decimal(row.total_amount or 0)
    
    # Build forecast days
    forecast_days = []
    total_revenue = Decimal(0)
    total_occupancy = 0
    peak_occupancy = 0
    peak_day = None
    lowest_occupancy = 100
    lowest_day = None
    days_with_data = 0
    
    current_date = today
    while current_date < end_date:
        inv = inventory_by_date.get(current_date, {"available": 0, "total": 0})
        total_rooms = inv["total"]
        available = inv["available"]
        booked = total_rooms - available  # Derived value
        
        occupancy = (booked / total_rooms * 100) if total_rooms > 0 else 0
        revenue = revenue_by_date.get(current_date, Decimal(0))
        
        forecast_days.append({
            "date": current_date,
            "occupancy_percent": round(occupancy, 1),
            "available_rooms": available,
            "booked_rooms": booked,
            "projected_revenue": revenue,
            "arrivals": arrivals_by_date.get(current_date, 0),
            "departures": departures_by_date.get(current_date, 0)
        })
        
        total_revenue += revenue
        
        if total_rooms > 0:  # Only count days with inventory data
            days_with_data += 1
            total_occupancy += occupancy
            
            if occupancy > peak_occupancy:
                peak_occupancy = occupancy
                peak_day = current_date
            
            if occupancy < lowest_occupancy:
                lowest_occupancy = occupancy
                lowest_day = current_date
        
        current_date += timedelta(days=1)
    
    avg_occupancy = total_occupancy / days_with_data if days_with_data > 0 else 0
    
    return {
        "forecast_days": forecast_days,
        "avg_occupancy": round(avg_occupancy, 1),
        "total_projected_revenue": total_revenue,
        "peak_day": peak_day,
        "lowest_day": lowest_day
    }


async def get_quick_stats(db: AsyncSession) -> dict:
    """
    Get quick financial metrics for dashboard header.
    
    Returns:
        Dictionary with revenue and occupancy metrics
    """
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    # Revenue today
    today_result = await db.execute(
        select(func.sum(Booking.total_amount)).where(
            and_(
                Booking.check_in == today,
                Booking.status == BookingStatus.CONFIRMED.value
            )
        )
    )
    revenue_today = Decimal(today_result.scalar() or 0)
    
    # Revenue MTD
    mtd_result = await db.execute(
        select(func.sum(Booking.total_amount)).where(
            and_(
                Booking.check_in >= month_start,
                Booking.check_in <= today,
                Booking.status == BookingStatus.CONFIRMED.value
            )
        )
    )
    revenue_mtd = Decimal(mtd_result.scalar() or 0)
    
    # Revenue YTD
    ytd_result = await db.execute(
        select(func.sum(Booking.total_amount)).where(
            and_(
                Booking.check_in >= year_start,
                Booking.check_in <= today,
                Booking.status == BookingStatus.CONFIRMED.value
            )
        )
    )
    revenue_ytd = Decimal(ytd_result.scalar() or 0)
    
    # Today's inventory for occupancy and RevPAR
    inventory_result = await db.execute(
        select(
            func.sum(Inventory.available_rooms).label('available'),
            func.sum(RoomType.total_rooms).label('total')
        ).join(
            RoomType, Inventory.room_type_id == RoomType.id
        ).where(Inventory.date == today)
    )
    inv = inventory_result.one()
    available = inv.available or 0
    total_rooms = inv.total or 0
    booked = total_rooms - available
    
    occupancy_today = (booked / total_rooms * 100) if total_rooms > 0 else 0
    
    # ADR - Average Daily Rate (Revenue / Rooms Sold)
    adr = revenue_today / booked if booked > 0 else Decimal(0)
    
    # RevPAR - Revenue Per Available Room
    revpar = revenue_today / total_rooms if total_rooms > 0 else Decimal(0)
    
    return {
        "revenue_today": revenue_today,
        "revenue_mtd": revenue_mtd,
        "revenue_ytd": revenue_ytd,
        "avg_daily_rate": round(adr, 2),
        "revpar": round(revpar, 2),
        "occupancy_today": round(occupancy_today, 1)
    }

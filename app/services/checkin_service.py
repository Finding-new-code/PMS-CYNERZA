"""
Digital Check-In service for online guest registration.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import secrets

from app.models.checkin import DigitalCheckIn, GuestDocument, CheckInStatus, DocumentType
from app.models.booking import Booking
from app.models.customer import Customer


async def create_checkin(
    db: AsyncSession,
    booking_id: int
) -> DigitalCheckIn:
    """Create a digital check-in for a booking."""
    # Check if already exists
    existing = await get_checkin_by_booking(db, booking_id)
    if existing:
        return existing
    
    # Get booking and customer info
    booking_query = select(Booking).options(
        selectinload(Booking.customer)
    ).where(Booking.id == booking_id)
    result = await db.execute(booking_query)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise ValueError("Booking not found")
    
    # Generate access token
    access_token = secrets.token_urlsafe(32)
    
    checkin = DigitalCheckIn(
        booking_id=booking_id,
        customer_id=booking.customer_id,
        status=CheckInStatus.NOT_STARTED,
        access_token=access_token,
        link_expires_at=datetime.utcnow() + timedelta(days=7),
        # Pre-fill from customer
        full_name=booking.customer.name if booking.customer else None,
        email=booking.customer.email if booking.customer else None,
        phone=booking.customer.phone if booking.customer else None
    )
    db.add(checkin)
    await db.commit()
    await db.refresh(checkin)
    return checkin


async def get_checkin_by_booking(
    db: AsyncSession,
    booking_id: int
) -> Optional[DigitalCheckIn]:
    """Get check-in by booking ID."""
    query = select(DigitalCheckIn).options(
        selectinload(DigitalCheckIn.documents)
    ).where(DigitalCheckIn.booking_id == booking_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_checkin_by_token(
    db: AsyncSession,
    access_token: str
) -> Optional[DigitalCheckIn]:
    """Get check-in by access token."""
    query = select(DigitalCheckIn).options(
        selectinload(DigitalCheckIn.documents),
        selectinload(DigitalCheckIn.booking)
    ).where(
        and_(
            DigitalCheckIn.access_token == access_token,
            DigitalCheckIn.link_expires_at > datetime.utcnow()
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_checkin(
    db: AsyncSession,
    checkin_id: int,
    updates: dict
) -> DigitalCheckIn:
    """Update check-in information."""
    query = select(DigitalCheckIn).where(DigitalCheckIn.id == checkin_id)
    result = await db.execute(query)
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        raise ValueError("Check-in not found")
    
    # Update status to in-progress if just started
    if checkin.status == CheckInStatus.NOT_STARTED:
        checkin.status = CheckInStatus.IN_PROGRESS
        checkin.started_at = datetime.utcnow()
    
    for key, value in updates.items():
        if value is not None and hasattr(checkin, key):
            setattr(checkin, key, value)
    
    await db.commit()
    await db.refresh(checkin)
    return checkin


async def capture_signature(
    db: AsyncSession,
    checkin_id: int,
    signature_image: str,
    ip_address: Optional[str] = None
) -> DigitalCheckIn:
    """Capture e-signature for check-in."""
    query = select(DigitalCheckIn).where(DigitalCheckIn.id == checkin_id)
    result = await db.execute(query)
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        raise ValueError("Check-in not found")
    
    checkin.signature_image = signature_image
    checkin.signature_captured_at = datetime.utcnow()
    checkin.signature_ip_address = ip_address
    checkin.terms_accepted = True
    checkin.terms_accepted_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(checkin)
    return checkin


async def complete_checkin(
    db: AsyncSession,
    checkin_id: int,
    signature_image: str,
    ip_address: Optional[str] = None
) -> DigitalCheckIn:
    """Complete the check-in process."""
    checkin = await capture_signature(db, checkin_id, signature_image, ip_address)
    
    checkin.status = CheckInStatus.COMPLETED
    checkin.completed_at = datetime.utcnow()
    
    # Sync data to customer profile
    if checkin.customer_id:
        customer_query = select(Customer).where(Customer.id == checkin.customer_id)
        result = await db.execute(customer_query)
        customer = result.scalar_one_or_none()
        
        if customer:
            if checkin.full_name:
                customer.name = checkin.full_name
            if checkin.email:
                customer.email = checkin.email
            if checkin.phone:
                customer.phone = checkin.phone
            if checkin.address:
                customer.address = checkin.address
    
    await db.commit()
    await db.refresh(checkin)
    return checkin


async def verify_checkin(
    db: AsyncSession,
    checkin_id: int,
    user_id: int,
    approve: bool,
    notes: Optional[str] = None
) -> DigitalCheckIn:
    """Staff verification of check-in."""
    query = select(DigitalCheckIn).where(DigitalCheckIn.id == checkin_id)
    result = await db.execute(query)
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        raise ValueError("Check-in not found")
    
    checkin.verified_by_id = user_id
    checkin.verified_at = datetime.utcnow()
    checkin.verification_notes = notes
    
    if approve:
        checkin.status = CheckInStatus.VERIFIED
    else:
        checkin.status = CheckInStatus.REJECTED
    
    await db.commit()
    await db.refresh(checkin)
    return checkin


# Document Functions
async def upload_document(
    db: AsyncSession,
    document_data: dict
) -> GuestDocument:
    """Upload a guest document."""
    # Get checkin for customer_id
    checkin_query = select(DigitalCheckIn).where(
        DigitalCheckIn.id == document_data.get("checkin_id")
    )
    result = await db.execute(checkin_query)
    checkin = result.scalar_one_or_none()
    
    if checkin:
        document_data["customer_id"] = checkin.customer_id
    
    document = GuestDocument(**document_data)
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def verify_document(
    db: AsyncSession,
    document_id: int,
    user_id: int,
    approve: bool,
    rejection_reason: Optional[str] = None
) -> GuestDocument:
    """Verify a guest document."""
    query = select(GuestDocument).where(GuestDocument.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise ValueError("Document not found")
    
    document.is_verified = approve
    document.verified_by_id = user_id
    document.verified_at = datetime.utcnow()
    
    if not approve:
        document.rejection_reason = rejection_reason
    
    await db.commit()
    await db.refresh(document)
    return document


async def get_checkin_summary(db: AsyncSession) -> dict:
    """Get check-in summary statistics."""
    # Total
    total_query = select(func.count(DigitalCheckIn.id))
    total = (await db.execute(total_query)).scalar() or 0
    
    # By status
    status_query = select(
        DigitalCheckIn.status,
        func.count(DigitalCheckIn.id)
    ).group_by(DigitalCheckIn.status)
    
    status_result = await db.execute(status_query)
    by_status = {row[0].value: row[1] for row in status_result}
    
    return {
        "total": total,
        "not_started": by_status.get("not_started", 0),
        "in_progress": by_status.get("in_progress", 0),
        "completed": by_status.get("completed", 0),
        "verified": by_status.get("verified", 0),
        "pending_verification": by_status.get("completed", 0)  # Completed but not verified
    }


async def get_pending_checkins(
    db: AsyncSession,
    limit: int = 50
) -> List[DigitalCheckIn]:
    """Get check-ins pending verification."""
    query = select(DigitalCheckIn).options(
        selectinload(DigitalCheckIn.booking),
        selectinload(DigitalCheckIn.documents)
    ).where(
        DigitalCheckIn.status == CheckInStatus.COMPLETED
    ).order_by(DigitalCheckIn.completed_at.desc()).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

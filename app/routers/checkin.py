"""
Digital Check-In API router for online guest registration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.core.config import get_settings
from app.schemas.checkin import (
    CheckInStart, CheckInUpdate, CheckInComplete, CheckInVerify, CheckInRead,
    DocumentUpload, DocumentVerify, DocumentRead,
    CheckInLink, CheckInSummary, CheckInStatusEnum, DocumentTypeEnum
)
from app.services import checkin_service
from app.models.checkin import CheckInStatus, DocumentType

router = APIRouter(prefix="/checkin", tags=["Digital Check-In"])

settings = get_settings()


# ============ Guest-Facing (Token-based) ============

@router.get("/guest/{access_token}", response_model=CheckInRead)
async def get_checkin_by_token(
    access_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get check-in form by access token (guest-facing, no auth required)."""
    checkin = await checkin_service.get_checkin_by_token(db, access_token)
    
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found or link expired")
    
    return CheckInRead(
        id=checkin.id,
        booking_id=checkin.booking_id,
        customer_id=checkin.customer_id,
        status=CheckInStatusEnum(checkin.status.value),
        full_name=checkin.full_name,
        email=checkin.email,
        phone=checkin.phone,
        date_of_birth=checkin.date_of_birth.date() if checkin.date_of_birth else None,
        nationality=checkin.nationality,
        address=checkin.address,
        estimated_arrival_time=checkin.estimated_arrival_time,
        special_requests=checkin.special_requests,
        has_signature=checkin.signature_image is not None,
        signature_captured_at=checkin.signature_captured_at,
        terms_accepted=checkin.terms_accepted,
        terms_accepted_at=checkin.terms_accepted_at,
        verified_by_id=checkin.verified_by_id,
        verified_at=checkin.verified_at,
        verification_notes=checkin.verification_notes,
        started_at=checkin.started_at,
        completed_at=checkin.completed_at,
        created_at=checkin.created_at
    )


@router.patch("/guest/{access_token}")
async def update_checkin_by_token(
    access_token: str,
    updates: CheckInUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update check-in form by access token (guest-facing)."""
    checkin = await checkin_service.get_checkin_by_token(db, access_token)
    
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found or link expired")
    
    updated = await checkin_service.update_checkin(
        db, checkin.id, updates.model_dump(exclude_unset=True)
    )
    
    return {"message": "Check-in updated", "status": updated.status.value}


@router.post("/guest/{access_token}/complete")
async def complete_checkin_by_token(
    access_token: str,
    complete_data: CheckInComplete,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Complete check-in and capture signature (guest-facing)."""
    checkin = await checkin_service.get_checkin_by_token(db, access_token)
    
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found or link expired")
    
    if not complete_data.terms_accepted:
        raise HTTPException(status_code=400, detail="Terms must be accepted")
    
    # Get client IP
    ip_address = request.client.host if request.client else None
    
    completed = await checkin_service.complete_checkin(
        db, checkin.id, complete_data.signature_image, ip_address
    )
    
    return {
        "message": "Check-in completed",
        "status": completed.status.value,
        "completed_at": completed.completed_at
    }


# ============ Staff-Facing (Authenticated) ============

@router.post("/", response_model=CheckInLink, status_code=status.HTTP_201_CREATED)
async def create_checkin(
    start_data: CheckInStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create digital check-in for a booking and generate guest link."""
    try:
        checkin = await checkin_service.create_checkin(db, start_data.booking_id)
        
        base_url = "http://localhost:3000"  # Frontend URL
        link_url = f"{base_url}/checkin/{checkin.access_token}"
        
        return CheckInLink(
            booking_id=checkin.booking_id,
            access_token=checkin.access_token,
            link_url=link_url,
            expires_at=checkin.link_expires_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/booking/{booking_id}", response_model=CheckInRead)
async def get_checkin_by_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get check-in by booking ID (staff)."""
    checkin = await checkin_service.get_checkin_by_booking(db, booking_id)
    
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    
    return CheckInRead(
        id=checkin.id,
        booking_id=checkin.booking_id,
        customer_id=checkin.customer_id,
        status=CheckInStatusEnum(checkin.status.value),
        full_name=checkin.full_name,
        email=checkin.email,
        phone=checkin.phone,
        date_of_birth=checkin.date_of_birth.date() if checkin.date_of_birth else None,
        nationality=checkin.nationality,
        address=checkin.address,
        estimated_arrival_time=checkin.estimated_arrival_time,
        special_requests=checkin.special_requests,
        has_signature=checkin.signature_image is not None,
        signature_captured_at=checkin.signature_captured_at,
        terms_accepted=checkin.terms_accepted,
        terms_accepted_at=checkin.terms_accepted_at,
        verified_by_id=checkin.verified_by_id,
        verified_at=checkin.verified_at,
        verification_notes=checkin.verification_notes,
        started_at=checkin.started_at,
        completed_at=checkin.completed_at,
        created_at=checkin.created_at
    )


@router.post("/{checkin_id}/verify")
async def verify_checkin(
    checkin_id: int,
    verify_data: CheckInVerify,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify a completed check-in (staff)."""
    try:
        checkin = await checkin_service.verify_checkin(
            db, checkin_id, current_user.id,
            verify_data.approve, verify_data.notes
        )
        
        return {
            "message": "Check-in verified" if verify_data.approve else "Check-in rejected",
            "status": checkin.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pending", response_model=List[CheckInRead])
async def get_pending_checkins(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get check-ins pending verification (staff)."""
    checkins = await checkin_service.get_pending_checkins(db, limit)
    
    return [
        CheckInRead(
            id=c.id,
            booking_id=c.booking_id,
            customer_id=c.customer_id,
            status=CheckInStatusEnum(c.status.value),
            full_name=c.full_name,
            email=c.email,
            phone=c.phone,
            date_of_birth=c.date_of_birth.date() if c.date_of_birth else None,
            nationality=c.nationality,
            address=c.address,
            estimated_arrival_time=c.estimated_arrival_time,
            special_requests=c.special_requests,
            has_signature=c.signature_image is not None,
            signature_captured_at=c.signature_captured_at,
            terms_accepted=c.terms_accepted,
            terms_accepted_at=c.terms_accepted_at,
            verified_by_id=c.verified_by_id,
            verified_at=c.verified_at,
            verification_notes=c.verification_notes,
            started_at=c.started_at,
            completed_at=c.completed_at,
            created_at=c.created_at
        )
        for c in checkins
    ]


@router.get("/summary", response_model=CheckInSummary)
async def get_checkin_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get check-in summary statistics."""
    summary = await checkin_service.get_checkin_summary(db)
    return CheckInSummary(**summary)


# ============ Documents ============

@router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    doc_data: DocumentUpload,
    db: AsyncSession = Depends(get_db)
):
    """Upload a guest document (can be called by guest via token)."""
    data = doc_data.model_dump()
    data["document_type"] = DocumentType(doc_data.document_type.value)
    
    document = await checkin_service.upload_document(db, data)
    
    return DocumentRead(
        id=document.id,
        checkin_id=document.checkin_id,
        document_type=DocumentTypeEnum(document.document_type.value),
        document_number=document.document_number,
        issuing_country=document.issuing_country,
        expiry_date=document.expiry_date.date() if document.expiry_date else None,
        file_name=document.file_name,
        file_type=document.file_type,
        file_path=document.file_path,
        is_verified=document.is_verified,
        verified_at=document.verified_at,
        rejection_reason=document.rejection_reason,
        uploaded_at=document.uploaded_at
    )


@router.post("/documents/{document_id}/verify")
async def verify_document(
    document_id: int,
    verify_data: DocumentVerify,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify a guest document (staff)."""
    try:
        document = await checkin_service.verify_document(
            db, document_id, current_user.id,
            verify_data.approve, verify_data.rejection_reason
        )
        
        return {
            "message": "Document verified" if verify_data.approve else "Document rejected",
            "is_verified": document.is_verified
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

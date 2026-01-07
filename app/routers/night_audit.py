"""
Night Audit API router for manual triggers and reports.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.night_audit import (
    NightAuditTrigger, NightAuditRead, NightAuditSummary,
    ReconciliationReport, RoomChargeRead
)
from app.services import night_audit_service

router = APIRouter(prefix="/night-audit", tags=["Night Audit"])


@router.post("/run", response_model=NightAuditRead, status_code=status.HTTP_201_CREATED)
async def trigger_night_audit(
    trigger_data: NightAuditTrigger,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger a night audit for a specific business date.
    """
    business_date = trigger_data.business_date or (datetime.utcnow().date() - timedelta(days=1))
    
    try:
        audit = await night_audit_service.run_night_audit(db, business_date, current_user.id)
        return NightAuditRead(
            id=audit.id,
            business_date=audit.business_date,
            started_at=audit.started_at,
            completed_at=audit.completed_at,
            is_completed=audit.is_completed,
            total_room_revenue=audit.total_room_revenue,
            total_other_revenue=audit.total_other_revenue,
            total_tax=audit.total_tax,
            total_payments=audit.total_payments,
            rooms_occupied=audit.rooms_occupied,
            rooms_available=audit.rooms_available,
            rooms_out_of_service=audit.rooms_out_of_service,
            occupancy_percentage=audit.occupancy_percentage,
            no_shows_processed=audit.no_shows_processed,
            no_show_revenue_lost=audit.no_show_revenue_lost,
            room_charges_posted=audit.room_charges_posted,
            notes=audit.notes,
            errors=audit.errors,
            run_by_id=audit.run_by_id,
            created_at=audit.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/audits", response_model=List[NightAuditRead])
async def list_night_audits(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List night audit records with pagination.
    """
    audits = await night_audit_service.list_audits(db, limit, offset)
    
    return [
        NightAuditRead(
            id=a.id,
            business_date=a.business_date,
            started_at=a.started_at,
            completed_at=a.completed_at,
            is_completed=a.is_completed,
            total_room_revenue=a.total_room_revenue,
            total_other_revenue=a.total_other_revenue,
            total_tax=a.total_tax,
            total_payments=a.total_payments,
            rooms_occupied=a.rooms_occupied,
            rooms_available=a.rooms_available,
            rooms_out_of_service=a.rooms_out_of_service,
            occupancy_percentage=a.occupancy_percentage,
            no_shows_processed=a.no_shows_processed,
            no_show_revenue_lost=a.no_show_revenue_lost,
            room_charges_posted=a.room_charges_posted,
            notes=a.notes,
            errors=a.errors,
            run_by_id=a.run_by_id,
            created_at=a.created_at
        )
        for a in audits
    ]


@router.get("/audits/{business_date}", response_model=NightAuditRead)
async def get_night_audit(
    business_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific night audit by business date.
    """
    audit = await night_audit_service.get_audit_by_date(db, business_date)
    
    if not audit:
        raise HTTPException(
            status_code=404,
            detail=f"No audit found for {business_date}"
        )
    
    return NightAuditRead(
        id=audit.id,
        business_date=audit.business_date,
        started_at=audit.started_at,
        completed_at=audit.completed_at,
        is_completed=audit.is_completed,
        total_room_revenue=audit.total_room_revenue,
        total_other_revenue=audit.total_other_revenue,
        total_tax=audit.total_tax,
        total_payments=audit.total_payments,
        rooms_occupied=audit.rooms_occupied,
        rooms_available=audit.rooms_available,
        rooms_out_of_service=audit.rooms_out_of_service,
        occupancy_percentage=audit.occupancy_percentage,
        no_shows_processed=audit.no_shows_processed,
        no_show_revenue_lost=audit.no_show_revenue_lost,
        room_charges_posted=audit.room_charges_posted,
        notes=audit.notes,
        errors=audit.errors,
        run_by_id=audit.run_by_id,
        created_at=audit.created_at
    )


@router.get("/reports/reconciliation/{business_date}", response_model=ReconciliationReport)
async def get_reconciliation_report(
    business_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate reconciliation report for a specific business date.
    """
    try:
        report_data = await night_audit_service.generate_reconciliation_report(db, business_date)
        return ReconciliationReport(**report_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/latest", response_model=NightAuditRead)
async def get_latest_audit(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the most recent night audit.
    """
    audit = await night_audit_service.get_latest_audit(db)
    
    if not audit:
        raise HTTPException(
            status_code=404,
            detail="No night audits found"
        )
    
    return NightAuditRead(
        id=audit.id,
        business_date=audit.business_date,
        started_at=audit.started_at,
        completed_at=audit.completed_at,
        is_completed=audit.is_completed,
        total_room_revenue=audit.total_room_revenue,
        total_other_revenue=audit.total_other_revenue,
        total_tax=audit.total_tax,
        total_payments=audit.total_payments,
        rooms_occupied=audit.rooms_occupied,
        rooms_available=audit.rooms_available,
        rooms_out_of_service=audit.rooms_out_of_service,
        occupancy_percentage=audit.occupancy_percentage,
        no_shows_processed=audit.no_shows_processed,
        no_show_revenue_lost=audit.no_show_revenue_lost,
        room_charges_posted=audit.room_charges_posted,
        notes=audit.notes,
        errors=audit.errors,
        run_by_id=audit.run_by_id,
        created_at=audit.created_at
    )

"""
Allotments API router.
Handles group reservations and inventory blocks.
"""

from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.allotment import Allotment, AllotmentStatus
from app.schemas.allotment import (
    AllotmentCreate,
    AllotmentResponse,
    AllotmentStatusUpdate,
    AllotmentPickupReport,
)
from app.services import allotment_service

router = APIRouter(prefix="/allotments", tags=["Allotments"])


@router.get("/", response_model=List[AllotmentResponse])
async def get_allotments(
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all allotments, optionally filtered by status.
    """
    query = select(Allotment)
    if status:
        query = query.where(Allotment.status == AllotmentStatus(status))
    
    result = await db.execute(query.order_by(Allotment.start_date.desc()))
    allotments = result.scalars().all()
    return allotments


@router.get("/{allotment_id}", response_model=AllotmentResponse)
async def get_allotment(
    allotment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific allotment by ID.
    """
    result = await db.execute(
        select(Allotment).where(Allotment.id == allotment_id)
    )
    allotment = result.scalar_one_or_none()
    if not allotment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allotment not found"
        )
    return allotment


@router.post("/", response_model=AllotmentResponse, status_code=status.HTTP_201_CREATED)
async def create_allotment(
    allotment_data: AllotmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new group allotment.
    """
    if allotment_data.end_date < allotment_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    room_allocations = [
        {"room_type_id": ra.room_type_id, "blocked_rooms": ra.blocked_rooms}
        for ra in allotment_data.room_allocations
    ]
    
    allotment = await allotment_service.create_allotment(
        db=db,
        name=allotment_data.name,
        start_date=allotment_data.start_date,
        end_date=allotment_data.end_date,
        room_allocations=room_allocations,
        cutoff_date=allotment_data.cutoff_date,
        contact_name=allotment_data.contact_name,
        contact_email=allotment_data.contact_email,
        contact_phone=allotment_data.contact_phone,
        group_rate=allotment_data.group_rate,
        notes=allotment_data.notes,
        created_by=current_user.id,
    )
    return allotment


@router.patch("/{allotment_id}/status", response_model=AllotmentResponse)
async def update_allotment_status(
    allotment_id: int,
    status_update: AllotmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the status of an allotment.
    Changing to DEFINITE will block rooms in inventory.
    Changing to RELEASED or CANCELLED will restore rooms.
    """
    allotment = await allotment_service.update_allotment_status(
        db, allotment_id, AllotmentStatus(status_update.status.value)
    )
    if not allotment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allotment not found"
        )
    return allotment


@router.get("/{allotment_id}/pickup-report", response_model=AllotmentPickupReport)
async def get_pickup_report(
    allotment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get pickup statistics for an allotment.
    """
    report = await allotment_service.get_allotment_pickup_report(db, allotment_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allotment not found"
        )
    return report


@router.post("/auto-release", response_model=dict)
async def trigger_auto_release(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger auto-release of allotments past cutoff date.
    """
    count = await allotment_service.auto_release_cutoff(db)
    return {"released_count": count}

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.pagination import PaginationParams

from app.db.session import get_db
from app.schemas.lead_schema import LeadCreate, LeadRead, LeadUpdate
from app.schemas.response import StandardResponse
from app.services.lead_service import (
    create_lead,
    list_leads,
    get_lead,
)


router = APIRouter()


@router.post("/", response_model=StandardResponse[LeadRead])
async def add_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    """Create a new lead"""
    return await create_lead(db, payload)


@router.get("/", response_model=StandardResponse)
async def get_leads(
    page: int = Query(1, description="Page number (starts from 1)"),
    size: int = Query(20, description="Items per page (max 100)"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
):
    """Get all leads with pagination"""
    pagination_params = PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_direction=sort_direction.lower() if sort_direction else "desc",
    )
    return await list_leads(db, pagination_params)


@router.get("/{lead_id}", response_model=StandardResponse[dict])
async def get_lead_by_id(lead_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single lead by ID"""
    return await get_lead(db, lead_id)

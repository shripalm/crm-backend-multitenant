from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from app.services.sitevisit_service import get_site_visit as get_site_visit_service
from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.schemas.sitevisite_schema import SiteVisitCreate, SiteVisitRead
from app.services.sitevisit_service import (
    create_site_visit,
    list_site_visit,
    update_site_visit,
)
from app.utils.pagination import PaginationParams

router = APIRouter()

@router.post("/", response_model = StandardResponse[SiteVisitRead])
async def add_site_visit(payload: SiteVisitCreate, db:AsyncSession = Depends(get_db)):
    """Create a new site visit"""
    return await create_site_visit(db, payload)


# List all site visits
@router.get("/", response_model=StandardResponse)
async def get_site_visit(
    page: int = Query(1, description="Page number (starts from 1)"),
    size: int = Query(20, description="Items per page (max 100)"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
):
    """Get all site visits with pagination"""
    pagination_params = PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_direction=sort_direction.lower() if sort_direction else "desc",
    )
    return await list_site_visit(db, pagination_params)

@router.get("/{site_visit_id}", response_model=StandardResponse[SiteVisitRead])
async def get_site_visit_by_id(site_visit_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single site visit by ID"""
    
    return await get_site_visit_service(db, site_visit_id)

@router.put("/{site_visit_id}", response_model=StandardResponse[SiteVisitRead])
async def update_site_visit_by_id(
    site_visit_id: UUID, payload: SiteVisitCreate, db: AsyncSession = Depends(get_db)
):
    """Update an existing site visit"""
    return await update_site_visit(db, site_visit_id, payload)
   
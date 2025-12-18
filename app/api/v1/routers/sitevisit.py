from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.services.sitevisit_service import get_site_visit as get_site_visit_service
from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.schemas.sitevisite_schema import SiteVisitCreate, SiteVisitRead
from app.services.sitevisit_service import (
    create_site_visit,
    list_site_visit,
    update_site_visit,
    
)

router = APIRouter()

@router.post("/", response_model = StandardResponse[SiteVisitRead])
async def add_site_visit(payload: SiteVisitCreate, db:AsyncSession = Depends(get_db)):
    """Create a new site visit"""
    return await create_site_visit(db, payload)


# List all site visits
@router.get("/", response_model=StandardResponse[list[SiteVisitRead]])
async def get_site_visit(db: AsyncSession = Depends(get_db)):
    """Get all site visit"""
    return await list_site_visit(db)

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
   
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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


@router.get("/", response_model=StandardResponse[list[LeadRead]])
async def get_leads(db: AsyncSession = Depends(get_db)):
    """Get all leads"""
    return await list_leads(db)


@router.get("/{lead_id}", response_model=StandardResponse[LeadRead])
async def get_lead_by_id(lead_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single lead by ID"""
    return await get_lead(db, lead_id)

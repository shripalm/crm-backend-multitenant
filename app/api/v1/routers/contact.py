from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.contact_schema import ContactCreate, ContactRead, ContactUpdate
from app.schemas.response import StandardResponse
from app.services.contact_service import (
    create_contact,
    list_contacts,
    get_contact,
    update_contact,
    delete_contact,
    backfill_unassigned_contacts,
)

from app.utils.pagination import PaginationParams
from fastapi import Query
router = APIRouter()


@router.post("/", response_model=StandardResponse[ContactRead])
async def add_contact(payload: ContactCreate, db: AsyncSession = Depends(get_db)):
    """Create a new contact"""
    return await create_contact(db, payload)


@router.get("/", response_model=StandardResponse)
async def get_contacts(
    page: int = Query(1, description="Page number (starts from 1)"),
    size: int = Query(20, description="Items per page (max 100)"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
):
    """Get all contacts with pagination"""
    pagination_params = PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_direction=sort_direction.lower() if sort_direction else "desc",
    )
    return await list_contacts(db, pagination_params)


@router.get("/{contact_id}", response_model=StandardResponse[ContactRead])
async def get_contact_by_id(contact_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single contact by ID"""
    return await get_contact(db, contact_id)


@router.put("/{contact_id}", response_model=StandardResponse[ContactRead])
async def update_contact_by_id(
    contact_id: UUID, payload: ContactUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an existing contact"""
    return await update_contact(db, contact_id, payload)


@router.delete("/{contact_id}", response_model=StandardResponse)
async def delete_contact_by_id(contact_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a contact"""
    return await delete_contact(db, contact_id)


@router.post("/backfill-tasks", response_model=StandardResponse)
async def backfill_tasks(db: AsyncSession = Depends(get_db)):
    """Create tasks for existing contacts that have no task assigned yet."""
    return await backfill_unassigned_contacts(db)

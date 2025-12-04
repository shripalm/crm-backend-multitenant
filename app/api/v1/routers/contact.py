from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.schemas.contact_schema import ContactCreate, ContactRead, ContactUpdate
from app.schemas.response import StandardResponse
from app.services.contact_service import (
    create_contact,
    list_contacts,
    get_contact,
    update_contact,
    delete_contact,
)

router = APIRouter()


@router.post("/", response_model=StandardResponse[ContactRead])
async def add_contact(payload: ContactCreate, db: AsyncSession = Depends(get_db)):
    """Create a new contact"""
    return await create_contact(db, payload)


@router.get("/", response_model=StandardResponse[list[ContactRead]])
async def get_contacts(db: AsyncSession = Depends(get_db)):
    """Get all contacts"""
    return await list_contacts(db)


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

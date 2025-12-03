from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.contact import Contact
from app.schemas.contact_schema import ContactRead, ContactCreate, ContactUpdate
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)


async def create_contact(db: AsyncSession, data: ContactCreate):
    """Create new contact and return serialized response."""
    try:
        contact = Contact(
            name=data.name,
            email=data.email,
            contact_no=data.contact_no,
            city=data.city,
            state=data.state,
            source=data.source,
            project_name=data.project_name,
            property_type=data.property_type,
            budget_range=data.budget_range,
        )

        db.add(contact)
        await db.commit()
        await db.refresh(contact)

        contact_data = ContactRead.model_validate(contact).model_dump()
        return success_response(data=contact_data, message="Contact created successfully")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to create contact: {str(e)}")


async def list_contacts(db: AsyncSession):
    """List all contacts and return serialized response."""
    try:
        stmt = select(Contact).order_by(Contact.created_at.desc())
        result = await db.execute(stmt)
        contacts = result.scalars().all()

        data = [ContactRead.model_validate(c).model_dump() for c in contacts]
        return success_response(data=data, message="Contacts retrieved successfully")

    except Exception as e:
        return internal_server_error(f"Failed to list contacts: {str(e)}")


async def get_contact(db: AsyncSession, contact_id: UUID):
    """Get a single contact by ID."""
    try:
        contact = await db.get(Contact, contact_id)
        
        if contact is None:
            return error_response(404, "Contact not found")

        contact_data = ContactRead.model_validate(contact).model_dump()
        return success_response(data=contact_data, message="Contact retrieved successfully")

    except Exception as e:
        return internal_server_error(f"Failed to get contact: {str(e)}")


async def update_contact(db: AsyncSession, contact_id: UUID, data: ContactUpdate):
    """Update an existing contact."""
    try:
        contact = await db.get(Contact, contact_id)
        
        if contact is None:
            return error_response(404, "Contact not found")

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(contact, field, value)

        await db.commit()
        await db.refresh(contact)

        contact_data = ContactRead.model_validate(contact).model_dump()
        return success_response(data=contact_data, message="Contact updated successfully")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to update contact: {str(e)}")


async def delete_contact(db: AsyncSession, contact_id: UUID):
    """Delete a contact by ID."""
    try:
        contact = await db.get(Contact, contact_id)
        
        if contact is None:
            return error_response(404, "Contact not found")

        await db.delete(contact)
        await db.commit()

        return success_response(data={"id": str(contact_id)}, message="Contact deleted successfully")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to delete contact: {str(e)}")

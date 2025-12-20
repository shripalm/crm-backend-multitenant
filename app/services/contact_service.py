from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from app.models.task_table import Task
from app.models.users import User
from app.utils.logging import logger

from app.models.contact import Contact
from app.schemas.contact_schema import ContactRead, ContactCreate, ContactUpdate
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)
from app.utils.pagination import (
    PaginationParams,
    ContactFilterParams,
    PaginatedResponse,
    get_paginator
)

from app.services.auto_assign_service import assign_task_for_contact_presales


async def _auto_assign_task_for_contact(db: AsyncSession, contact: Contact) -> None:
    """Auto-assign a new task for the given contact to an active user.
    
    Logic:
    - First try to assign to users in 'presales' team (case-insensitive)
    - If no presales users, fall back to any active users
    - Assign to user with fewest tasks (ties broken by user id)
    - Always set assigned_to_team='presales' as requested
    """
    try:
        await assign_task_for_contact_presales(db, contact)
    except Exception as e:
        print(f"Error in auto-assign wrapper: {str(e)}")


async def create_contact(db: AsyncSession, data: ContactCreate):
    """Create new contact and return serialized response."""
    try:
        logger.info("Creating contact", name=data.name)
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

        # Auto-assign task to an active presales user based on least load
        await _auto_assign_task_for_contact(db, contact)

        contact_data = ContactRead.model_validate(contact).model_dump()
        logger.info("Contact created successfully", contact_id=str(contact.id))
        return success_response(data=contact_data, message="Contact created successfully")

    except Exception as e:
        logger.error(f"Failed to create contact: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to create contact: {str(e)}")


async def list_contacts(
    db: AsyncSession,
    pagination_params: PaginationParams,
    filter_params: Optional[ContactFilterParams] = None
):
    """
    List contacts with pagination, filtering, and sorting
    """
    try:
        paginator = get_paginator(db)
        
        # Build base query
        query = select(Contact).options(selectinload(Contact.call_reports))
        
        # Get paginated results
        result = await paginator.paginate(
            query=query,
            pagination_params=pagination_params,
            filter_params=filter_params,
            model_class=Contact
        )
        
        # Convert contacts to schema format
        contacts_data = [
            ContactRead.model_validate(contact).model_dump() 
            for contact in result.data
        ]
        
        # Build paginated response
        paginated_response = PaginatedResponse[ContactRead](
            data=contacts_data,
            meta=result.meta,
            message="Contacts retrieved successfully"
        )
        
        logger.info(
            "Retrieved paginated contacts",
            page=pagination_params.page,
            size=pagination_params.size,
            total=result.meta.total_items
        )
        
        return success_response(
            data=paginated_response.model_dump(),
            message="Contacts retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to list contacts with pagination: {str(e)}")
        return internal_server_error(f"Failed to list contacts: {str(e)}")


async def get_contact(db: AsyncSession, contact_id: UUID):
    """Get a single contact by ID."""
    try:
        contact = await db.get(Contact, contact_id)
        
        if contact is None:
            logger.warning("Contact not found", contact_id=str(contact_id))
            return error_response(404, "Contact not found")

        contact_data = ContactRead.model_validate(contact).model_dump()
        logger.debug("Fetched contact", contact_id=str(contact_id))
        return success_response(data=contact_data, message="Contact retrieved successfully")

    except Exception as e:
        logger.error(f"Failed to get contact: {str(e)}")
        return internal_server_error(f"Failed to get contact: {str(e)}")


async def update_contact(db: AsyncSession, contact_id: UUID, data: ContactUpdate):
    """Update an existing contact."""
    try:
        contact = await db.get(Contact, contact_id)
        
        if contact is None:
            return error_response(404, "Contact not found")

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Contact update payload", contact_id=str(contact_id), update_data=update_data)
        
        for field, value in update_data.items():
            setattr(contact, field, value)

        await db.commit()
        await db.refresh(contact)

        contact_data = ContactRead.model_validate(contact).model_dump()
        logger.info("Contact updated", contact_id=str(contact_id))
        return success_response(data=contact_data, message="Contact updated successfully")

    except Exception as e:
        logger.error(f"Failed to update contact: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to update contact: {str(e)}")


async def delete_contact(db: AsyncSession, contact_id: UUID):
    """Delete a contact by ID."""
    try:
        contact = await db.get(Contact, contact_id)
        
        if contact is None:
            logger.warning("Contact not found for delete", contact_id=str(contact_id))
            return error_response(404, "Contact not found")

        await db.delete(contact)
        await db.commit()

        logger.info("Contact deleted", contact_id=str(contact_id))
        return success_response(data={"id": str(contact_id)}, message="Contact deleted successfully")

    except Exception as e:
        logger.error(f"Failed to delete contact: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to delete contact: {str(e)}")


async def backfill_unassigned_contacts(db: AsyncSession):
    """Create tasks for contacts that currently have no task.

    This can be run once to ensure legacy contacts are assigned.
    """
    try:
        # Find contacts with no task referencing them
        subq = (
            select(Task.lead_id)
            .where(Task.lead_id.is_not(None))
            .subquery()
        )

        stmt = select(Contact).where(~Contact.id.in_(select(subq.c.lead_id)))
        result = await db.execute(stmt)
        contacts = result.scalars().all()

        created = 0
        for contact in contacts:
            await _auto_assign_task_for_contact(db, contact)
            created += 1

        return success_response(data={"created": created}, message="Backfill completed")
    except Exception as e:
        return internal_server_error(f"Failed to backfill tasks: {str(e)}")

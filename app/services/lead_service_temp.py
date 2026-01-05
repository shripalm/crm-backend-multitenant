from typing import Any, Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils.pagination import (
    PaginationParams,
    PaginatedResponse,
    get_paginator,
    T
)

from app.models.leads import Lead
from app.models.contact import Contact
from app.models.users import User
from app.schemas.lead_schema import LeadRead, LeadCreate, LeadUpdate
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)

from app.services.auto_assign_service import assign_task_for_lead_site_visit
from app.utils.logging import logger


async def create_lead(db: AsyncSession, data: LeadCreate):
    try:
        lead = Lead(
            assigned_at=data.assigned_at,
            contact_id=data.contact_id,
            sales_task_id=data.sales_task_id,
            remark=data.remark,
            site_visit=data.site_visit,
            last_visited_date=data.last_visited_date,
            call_duration=data.call_duration,
            employee_id=data.employee_id,
        )

        db.add(lead)
        await db.commit()
        await db.refresh(lead)

        await assign_task_for_lead_site_visit(db, lead)

        lead_data = LeadRead.model_validate(lead).model_dump()
        return success_response(data=lead_data, message="Lead created successfully")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to create lead: {str(e)}")


async def list_leads(
    db: AsyncSession,
    pagination_params: PaginationParams,
):
    """List all leads with pagination and related data."""
    try:
        # First, get paginated lead IDs
        lead_query = select(Lead.id).order_by(Lead.created_at.desc())
        paginator = get_paginator(db)
        paginated_result = await paginator.paginate(
            query=lead_query,
            pagination_params=pagination_params,
            model_class=Lead
        )
        
        # Get the paginated lead IDs
        lead_ids = [str(lead.id) for lead in paginated_result.data]
        
        if not lead_ids:
            return success_response(
                data={"data": [], "meta": paginated_result.meta},
                message="No leads found"
            )
        
        # Now fetch the full lead data with joins for just these IDs
        stmt = (
            select(Lead, Contact, User)
            .join(Contact, Lead.contact_id == Contact.id, isouter=True)
            .join(User, Lead.employee_id == User.id, isouter=True)
            .where(Lead.id.in_(lead_ids))
            .order_by(Lead.created_at.desc())
        )
        
        result = await db.execute(stmt)
        rows = result.unique().all()
        
        # Create a mapping of lead ID to its data
        lead_data_map = {
            str(lead.id): {
                "id": str(lead.id),
                "created_at": lead.created_at,
                "assigned_at": lead.assigned_at,
                "remark": lead.remark,
                "site_visit": lead.site_visit,
                "last_visited_date": lead.last_visited_date,
                "call_duration": lead.call_duration,
                "contact_name": contact.name if contact else None,
                "contact": contact.contact_no if contact else None,
                "source": contact.source if contact else None,
                "project_name": contact.project_name if contact else None,
                "property_type": contact.property_type if contact else None,
                "budget_range": contact.budget_range if contact else None,
                "employee_name": user.full_name if user else None,
            }
            for lead, contact, user in rows
        }
        
        # Maintain the original order from pagination
        data = [lead_data_map[lead_id] for lead_id in lead_ids if lead_id in lead_data_map]
        
        return success_response(
            data={
                "data": data,
                "meta": paginated_result.meta
            },
            message="Leads retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to list leads: {str(e)}", exc_info=True)
        return internal_server_error(f"Failed to list leads: {str(e)}")


async def get_lead(db: AsyncSession, lead_id: UUID):
    try:
        stmt = (
            select(Lead, Contact, User)
            .join(Contact, Lead.contact_id == Contact.id, isouter=True)
            .join(User, Lead.employee_id == User.id, isouter=True)
            .where(Lead.id == lead_id)
        )
        
        result = await db.execute(stmt)
        row = result.unique().first()
        
        if not row:
            return error_response(404, "Lead not found")
        
        lead, contact, user = row
        
        lead_data = {
            "id": str(lead.id),
            "created_at": lead.created_at,
            "assigned_at": lead.assigned_at,
            "remark": lead.remark,
            "site_visit": lead.site_visit,
            "last_visited_date": lead.last_visited_date,
            "call_duration": lead.call_duration,
            "contact_name": contact.name if contact else None,
            "contact": contact.contact_no if contact else None,
            "source": contact.source if contact else None,
            "project_name": contact.project_name if contact else None,
            "property_type": contact.property_type if contact else None,
            "budget_range": contact.budget_range if contact else None,
            "employee_name": user.full_name if user else None,
        }
        
        return success_response(data=lead_data, message="Lead retrieved successfully")
        
    except Exception as e:
        return internal_server_error(f"Failed to get lead: {str(e)}")


async def update_lead(db: AsyncSession, lead_id: UUID, data: LeadUpdate):
    try:
        lead = await db.get(Lead, lead_id)
        if not lead:
            return error_response(404, "Lead not found")
        
        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lead, field, value)
        
        await db.commit()
        await db.refresh(lead)
        
        lead_data = LeadRead.model_validate(lead).model_dump()
        return success_response(data=lead_data, message="Lead updated successfully")
        
    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to update lead: {str(e)}")


async def delete_lead(db: AsyncSession, lead_id: UUID):
    try:
        lead = await db.get(Lead, lead_id)
        if not lead:
            return error_response(404, "Lead not found")
        
        await db.delete(lead)
        await db.commit()
        
        return success_response(message="Lead deleted successfully")
        
    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to delete lead: {str(e)}")

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.leads import Lead
from app.schemas.lead_schema import LeadRead, LeadCreate, LeadUpdate
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)

from app.services.auto_assign_service import assign_task_for_lead_site_visit


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


async def list_leads(db: AsyncSession):
    try:
        stmt = select(Lead).order_by(Lead.created_at.desc())
        result = await db.execute(stmt)
        leads = result.scalars().all()

        data = [LeadRead.model_validate(l).model_dump() for l in leads]
        return success_response(data=data, message="Leads retrieved successfully")
    except Exception as e:
        return internal_server_error(f"Failed to list leads: {str(e)}")


async def get_lead(db: AsyncSession, lead_id: UUID):
    try:
        lead = await db.get(Lead, lead_id)
        if lead is None:
            return error_response(404, "Lead not found")

        lead_data = LeadRead.model_validate(lead).model_dump()
        return success_response(data=lead_data, message="Lead retrieved successfully")
    except Exception as e:
        return internal_server_error(f"Failed to get lead: {str(e)}")


async def update_lead(db: AsyncSession, lead_id: UUID, data: LeadUpdate):
    try:
        lead = await db.get(Lead, lead_id)
        if lead is None:
            return error_response(404, "Lead not found")

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
        if lead is None:
            return error_response(404, "Lead not found")

        await db.delete(Lead)
        await db.commit()

        return success_response(data={"id": str(lead_id)}, message="Lead deleted successfully")
    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to delete lead: {str(e)}")

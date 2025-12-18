from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.callreport import CallReport
from app.models.contact import Contact
from app.schemas.callreport_schema import CallReportRead, CallReportCreate, CallReportUpdate
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)

from app.services.auto_assign_service import assign_task_for_call_report_sales


async def create_call_report(db: AsyncSession, data: CallReportCreate):
    """Create new call report and return serialized response."""
    try:
        call_report = CallReport(
            contact_id=data.contact_id,
            tags=data.tags,
            sales_agent=data.sales_agent,
            assigned_date=data.assigned_date,
            last_activity_date=data.last_activity_date,
            remark=data.remark,
            status=data.status,
            source=data.source,
            employee_id=data.employee_id,
            call_duration=data.call_duration,
            next_follow_up=data.next_follow_up,
        )

        db.add(call_report)
        await db.commit()
        await db.refresh(call_report)

        await assign_task_for_call_report_sales(db, call_report)

        call_report_data = CallReportRead.model_validate(call_report).model_dump()
        return success_response(data=call_report_data, message="Call report created successfully")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to create call report: {str(e)}")


async def list_call_reports(db: AsyncSession):
    """List all call reports and return serialized response."""
    try:
        stmt = (
            select(CallReport, Contact)
            .join(Contact, CallReport.contact_id == Contact.id, isouter=True)
            .order_by(CallReport.created_at.desc())
        )

        result = await db.execute(stmt)
        rows = result.all()

        data: list[dict[str, Any]] = []
        for cr, contact in rows:
            item = {
                "id": str(cr.id),
                "created_at": cr.created_at,
                "updated_at": cr.updated_at,
                "tags": cr.tags,
                "sales_agent": cr.sales_agent,
                "assigned_date": cr.assigned_date,
                "last_activity_date": cr.last_activity_date,
                "remark": cr.remark,
                "status": cr.status,
                "source": cr.source,
                "call_duration": cr.call_duration,
                "next_follow_up": cr.next_follow_up,
                # Contact details
                "name": contact.name if contact else None,
                "contact": contact.contact_no if contact else None,
                "email": contact.email if contact else None,
                "city": contact.city if contact else None,
                "state": contact.state if contact else None,
                "project_name": contact.project_name if contact else None,
                "property_type": contact.property_type if contact else None,
                "budget_range": contact.budget_range if contact else None,
            }
            data.append(item)
        return success_response(data=data, message="Call reports retrieved successfully")

    except Exception as e:
        return internal_server_error(f"Failed to list call reports: {str(e)}")


async def get_call_report(db: AsyncSession, call_report_id: UUID):
    """Get a single call report by ID."""
    try:
        stmt = (
            select(CallReport, Contact)
            .join(Contact, CallReport.contact_id == Contact.id, isouter=True)
            .where(CallReport.id == call_report_id)
        )

        result = await db.execute(stmt)
        row = result.first()

        if row is None:
            return error_response(404, "Call report not found")

        cr, contact = row

        call_report_data: dict[str, Any] = {
            "id": str(cr.id),
            "created_at": cr.created_at,
            "updated_at": cr.updated_at,
            "tags": cr.tags,
            "sales_agent": cr.sales_agent,
            "assigned_date": cr.assigned_date,
            "last_activity_date": cr.last_activity_date,
            "remark": cr.remark,
            "status": cr.status,
            "source": cr.source,
            "call_duration": cr.call_duration,
            "next_follow_up": cr.next_follow_up,
            # Contact details
            "name": contact.name if contact else None,
            "contact": contact.contact_no if contact else None,
            "email": contact.email if contact else None,
            "city": contact.city if contact else None,
            "state": contact.state if contact else None,
            "project_name": contact.project_name if contact else None,
            "property_type": contact.property_type if contact else None,
            "budget_range": contact.budget_range if contact else None,
        }

        return success_response(data=call_report_data, message="Call report retrieved successfully")

    except Exception as e:
        return internal_server_error(f"Failed to get call report: {str(e)}")


async def update_call_report(db: AsyncSession, call_report_id: UUID, data: CallReportUpdate):
    """Update an existing call report."""
    try:
        call_report = await db.get(CallReport, call_report_id)
        
        if call_report is None:
            return error_response(404, "Call report not found")

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(call_report, field, value)

        await db.commit()
        await db.refresh(call_report)

        call_report_data = CallReportRead.model_validate(call_report).model_dump()
        return success_response(data=call_report_data, message="Call report updated successfully")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to update call report: {str(e)}")


async def delete_call_report(db: AsyncSession, call_report_id: UUID):
    """Delete a call report by ID."""
    try:
        call_report = await db.get(CallReport, call_report_id)
        
        if call_report is None:
            return error_response(404, "Call report not found")

        await db.delete(call_report)
        await db.commit()

        return success_response(data={"id": str(call_report_id)}, message="Call report deleted successfully")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to delete call report: {str(e)}")

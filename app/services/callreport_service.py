from typing import Any, Optional, List
from uuid import UUID

from app.utils.pagination import T

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from app.utils.logging import logger

from app.models.callreport import CallReport
from app.models.contact import Contact
from app.models.users import User
from app.schemas.callreport_schema import CallReportRead, CallReportCreate, CallReportUpdate
from app.schemas.callreport_stats_schema import CallReportStatsData
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)
from app.utils.pagination import (
    PaginationParams,
    PaginatedResponse,
    get_paginator
)

from app.services.auto_assign_service import assign_task_for_call_report_sales


async def get_call_report_stats(
    db: AsyncSession,
    date_from=None,
    date_to=None,
    employee_id: Optional[UUID] = None,
):
    try:
        filters = []
        if employee_id:
            filters.append(CallReport.employee_id == employee_id)
        if date_from:
            filters.append(func.date(CallReport.created_at) >= date_from)
        if date_to:
            filters.append(func.date(CallReport.created_at) <= date_to)

        stmt = (
            select(
                CallReport.employee_id.label("employee_id"),
                User.full_name.label("full_name"),
                func.count(CallReport.id).label("total_calls"),
                func.coalesce(func.avg(CallReport.call_duration), 0).label(
                    "avg_call_duration_seconds"
                ),
            )
            .select_from(CallReport)
            .join(User, User.id == CallReport.employee_id, isouter=True)
        )
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.group_by(CallReport.employee_id, User.full_name)
        stmt = stmt.order_by(func.count(CallReport.id).desc())

        result = await db.execute(stmt)
        rows = result.all()

        daily_stmt = (
            select(
                CallReport.employee_id.label("employee_id"),
                func.date(CallReport.created_at).label("call_date"),
                func.count(CallReport.id).label("count"),
            )
            .select_from(CallReport)
        )
        if filters:
            daily_stmt = daily_stmt.where(*filters)
        daily_stmt = daily_stmt.group_by(
            CallReport.employee_id,
            func.date(CallReport.created_at),
        )

        daily_result = await db.execute(daily_stmt)
        daily_rows = daily_result.all()

        daily_map: dict[str, dict] = {}
        for r in daily_rows:
            key = str(r.employee_id) if r.employee_id else "None"
            if key not in daily_map:
                daily_map[key] = {}
            daily_map[key][r.call_date] = int(r.count or 0)

        users = []
        total_calls = 0
        for r in rows:
            key = str(r.employee_id) if r.employee_id else "None"
            total_calls += int(r.total_calls or 0)
            users.append(
                {
                    "employee_id": r.employee_id,
                    "full_name": r.full_name,
                    "total_calls": int(r.total_calls or 0),
                    "avg_call_duration_seconds": float(
                        r.avg_call_duration_seconds or 0
                    ),
                    "daily_counts": daily_map.get(key, {}),
                }
            )

        payload = CallReportStatsData(
            total_calls=total_calls,
            total_users=len(users),
            date_from=date_from,
            date_to=date_to,
            users=users,
        ).model_dump()

        return success_response(data=payload, message="Call report stats retrieved successfully")
    except Exception as e:
        logger.error(f"Failed to get call report stats: {str(e)}", exc_info=True)
        return internal_server_error(f"Failed to get call report stats: {str(e)}")


async def create_call_report(db: AsyncSession, data: CallReportCreate):
    """Create new call report and return serialized response."""
    try:
        logger.info("Creating call report", contact_id=str(data.contact_id))
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

        call_report_data = CallReportRead.model_validate(
            call_report).model_dump()
        logger.info("Call report created successfully",
                    call_report_id=str(call_report.id))
        return success_response(data=call_report_data, message="Call report created successfully")

    except Exception as e:
        logger.error(f"Failed to create call report: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to create call report: {str(e)}")


async def list_call_reports(
    db: AsyncSession,
    pagination_params: PaginationParams = PaginationParams(),
):
    """List all call reports with pagination and related contact data."""
    try:
        # First, get paginated call report IDs
        report_query = select(CallReport.id).order_by(CallReport.created_at.desc())
        paginator = get_paginator(db)
        paginated_result = await paginator.paginate(
            query=report_query,
            pagination_params=pagination_params,
            model_class=CallReport
        )
        
        # Get the paginated report IDs
        report_ids = [str(report) for report in paginated_result.data]
        
        if not report_ids:
            return success_response(
                data={"data": [], "meta": paginated_result.meta},
                message="No call reports found"
            )
        
        # Now fetch the full report data with contact joins for just these IDs
        stmt = (
            select(CallReport, Contact)
            .join(Contact, CallReport.contact_id == Contact.id, isouter=True)
            .where(CallReport.id.in_(report_ids))
            .order_by(CallReport.created_at.desc())
        )
        
        result = await db.execute(stmt)
        rows = result.unique().all()
        
        # Create a mapping of report ID to its data
        report_data_map = {
            str(cr.id): {
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
            for cr, contact in rows
        }
        
        # Maintain the original order from pagination
        data = [report_data_map[report_id] for report_id in report_ids if report_id in report_data_map]
        
        return success_response(
            data={
                "data": data,
                "meta": paginated_result.meta
            },
            message="Call reports retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to list call reports: {str(e)}", exc_info=True)
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
        logger.error(f"Failed to get call report: {str(e)}")
        return internal_server_error(f"Failed to get call report: {str(e)}")


async def update_call_report(db: AsyncSession, call_report_id: UUID, data: CallReportUpdate):
    """Update an existing call report."""
    try:
        call_report = await db.get(CallReport, call_report_id)

        if call_report is None:
            logger.warning("Call report not found for update",
                           call_report_id=str(call_report_id))
            return error_response(404, "Call report not found")

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Call report update payload", call_report_id=str(
            call_report_id), update_data=update_data)

        for field, value in update_data.items():
            setattr(call_report, field, value)

        await db.commit()
        await db.refresh(call_report)

        call_report_data = CallReportRead.model_validate(
            call_report).model_dump()
        logger.info("Call report updated", call_report_id=str(call_report_id))
        return success_response(data=call_report_data, message="Call report updated successfully")

    except Exception as e:
        logger.error(f"Failed to update call report: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to update call report: {str(e)}")


async def delete_call_report(db: AsyncSession, call_report_id: UUID):
    """Delete a call report by ID."""
    try:
        call_report = await db.get(CallReport, call_report_id)

        if call_report is None:
            logger.warning("Call report not found for delete",
                           call_report_id=str(call_report_id))
            return error_response(404, "Call report not found")

        await db.delete(call_report)
        await db.commit()

        logger.info("Call report deleted", call_report_id=str(call_report_id))
        return success_response(data={"id": str(call_report_id)}, message="Call report deleted successfully")

    except Exception as e:
        logger.error(f"Failed to delete call report: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to delete call report: {str(e)}")

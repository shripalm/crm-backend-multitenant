from http.client import HTTPException
from typing import Any, Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.utils.logging import logger

from app.models.sitevisit import SiteVisit
from app.models.contact import Contact
from app.models.users import User
from app.schemas.sitevisite_schema import SiteVisitCreate, SiteVisitRead, SiteVisitUpdate
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)
from app.utils.pagination import (
    PaginationParams,
    PaginatedResponse,
    get_paginator,
    T
)

async def create_site_visit(db: AsyncSession, data: SiteVisitCreate):
    try:
        logger.info("Creating Site Visit", employee_id=str(data.employee_id), contact_id=str(data.contact_id))
        site_visit = SiteVisit(
            employee_id = data.employee_id,
            contact_id = data.contact_id,
            visit_frequency = data.visit_frequency,
            schedule_date = data.schedule_date,
            remark = data.remark,
            lead_id = data.lead_id,
            last_visited_date = data.last_visited_date,
        )

        db.add(site_visit)
        await db.commit()
        await db.refresh(site_visit)

        site_visit_data = SiteVisitRead.model_validate(site_visit).model_dump()
        logger.info("Site Visit created successfully", site_visit_id = str(site_visit.id))
        return success_response(data=site_visit_data, message="Site Visit created successfully")

    except Exception as e:
        logger.error(f"Failed to create site visit:{str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to create site visit:{str(e)}")
    
async def list_site_visit(
    db: AsyncSession,
    pagination_params: PaginationParams = PaginationParams(),
):
    """List all site visits with pagination and related data."""
    try:
        # First, get paginated site visit IDs
        visit_query = select(SiteVisit.id).order_by(SiteVisit.created_at.desc())
        paginator = get_paginator(db)
        paginated_result = await paginator.paginate(
            query=visit_query,
            pagination_params=pagination_params,
            model_class=SiteVisit
        )
        
        # Get the paginated visit IDs
        visit_ids = [str(visit) for visit in paginated_result.data]
        
        if not visit_ids:
            return success_response(
                data={"data": [], "meta": paginated_result.meta},
                message="No site visits found"
            )
        
        # Now fetch the full visit data with joins for just these IDs
        stmt = (
            select(SiteVisit, Contact, User)
            .join(Contact, SiteVisit.contact_id == Contact.id, isouter=True)
            .join(User, SiteVisit.employee_id == User.id, isouter=True)
            .where(SiteVisit.id.in_(visit_ids))
            .order_by(SiteVisit.created_at.desc())
        )
        
        result = await db.execute(stmt)
        rows = result.unique().all()
        
        # Create a mapping of visit ID to its data
        visit_data_map = {
            str(visit.id): {
                "id": str(visit.id),
                "created_at": visit.created_at,
                "visit_frequency": visit.visit_frequency,
                "schedule_date": visit.schedule_date,
                "remark": visit.remark,
                # "lead_id": str(visit.lead_id) if visit.lead_id else None,
                "last_visited_date": visit.last_visited_date,
                # Contact details
                "contact_name": contact.name if contact else None,
                "contact_number": contact.contact_no if contact else None,
                "email": contact.email if contact else None,
                "city": contact.city if contact else None,
                "state": contact.state if contact else None,
                "project_name": contact.project_name if contact else None,
                "property_type": contact.property_type if contact else None,
                "budget_range": contact.budget_range if contact else None,
                # Employee details
                "employee_name": user.full_name if user else None,
                "employee_email": user.email if user else None,
            }
            for visit, contact, user in rows
        }
        
        # Maintain the original order from pagination
        data = [visit_data_map[visit_id] for visit_id in visit_ids if visit_id in visit_data_map]
        
        return success_response(
            data={
                "data": data,
                "meta": paginated_result.meta
            },
            message="Site visits retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to list site visits: {str(e)}", exc_info=True)
        return internal_server_error(f"Failed to list site visits: {str(e)}")
    

async def get_site_visit(db: AsyncSession, site_visit_id: UUID):
    """Get a single site visit by ID with related data."""
    try:
        # Fetch site visit with joins to Contact and User
        stmt = (
            select(SiteVisit, Contact, User)
            .join(Contact, SiteVisit.contact_id == Contact.id, isouter=True)
            .join(User, SiteVisit.employee_id == User.id, isouter=True)
            .where(SiteVisit.id == site_visit_id)
        )
        
        result = await db.execute(stmt)
        row = result.first()
        
        if not row:
            logger.warning("Site visit not found", extra={"site_visit_id": str(site_visit_id)})
            return error_response(404, "Site visit not found")
            
        site_visit, contact, user = row
        
        site_visit_data = {
            "id": str(site_visit.id),
            "created_at": site_visit.created_at,
            "visit_frequency": site_visit.visit_frequency,
            "schedule_date": site_visit.schedule_date,
            "remark": site_visit.remark,
            "lead_id": str(site_visit.lead_id) if site_visit.lead_id else None,
            "last_visited_date": site_visit.last_visited_date,
            # Contact details
            "contact": {
                "id": str(contact.id) if contact else None,
                "name": contact.name if contact else None,
                "contact_no": contact.contact_no if contact else None,
                "email": contact.email if contact else None,
                "city": contact.city if contact else None,
                "state": contact.state if contact else None,
                "project_name": contact.project_name if contact else None,
                "property_type": contact.property_type if contact else None,
                "budget_range": contact.budget_range if contact else None,
            },
            # Employee details
            "employee": {
                "id": str(user.id) if user else None,
                "name": user.full_name if user else None,
                "email": user.email if user else None,
                "contact": user.contact if user else None,
            } if user else None
        }

        logger.info("Site visit retrieved successfully", extra={"site_visit_id": str(site_visit_id)})
        return success_response(
            data=site_visit_data,
            message="Site visit retrieved successfully"
        )
        
    except Exception as e:
        logger.error(
            f"Failed to get site visit: {str(e)}",
            exc_info=True,
            extra={"site_visit_id": str(site_visit_id)}
        )
        return internal_server_error(f"Failed to get site visit: {str(e)}")

async def update_site_visit(db: AsyncSession, site_visit_id: UUID, data: SiteVisitUpdate):
    try:
        site_visit = await db.get(SiteVisit, site_visit_id)

        if site_visit is None:
            logger.warning("Site Visit not found for update", site_visit_id=str(site_visit_id))
            return error_response(404, "Site Visit not found")
        
        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Site Visit update data", site_visit_id=str(site_visit_id), update_data=update_data)

        for field, value in update_data.items():
            setattr(site_visit, field, value)

        await db.commit()
        await db.refresh(site_visit)

        site_visit_data = SiteVisitRead.model_validate(site_visit).model_dump()
        logger.info("Site Visit updated successfully", site_visit_id=str(site_visit_id))
        return success_response(data=site_visit_data, message="Site Visit updated successfully")
    
    except Exception as e:
        logger.error(f"Failed to update site visit: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to update site visit: {str(e)}")
from http.client import HTTPException
from typing import Any, Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.utils.logging import logger

from app.models.sitevisit import SiteVisit
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
    pagination_params: PaginationParams,
):
    """List all site visits and return serialized response."""
    try:
        paginator = get_paginator(db)
        query = select(SiteVisit).order_by(SiteVisit.created_at.desc())
        result = await paginator.paginate(
            query=query,
            pagination_params=pagination_params,
            model_class=SiteVisit
        )
        site_visit_data = [SiteVisitRead.model_validate(sv).model_dump() for sv in result.data]
        paginated_response = PaginatedResponse[SiteVisitRead](
            data=site_visit_data,
            meta=result.meta,
            message="Site Visit retrieved successfully"
        )
        return success_response(data=paginated_response.model_dump(), message="Site Visit retrieved successfully")
    except Exception as e:
        logger.error(f"Failed to list site visit:{str(e)}")
        return internal_server_error(f"Failed to list site visit: {str(e)}")
    

async def get_site_visit(db: AsyncSession, site_visit_id: UUID):
    try:
        # Fetch site visit by primary key
        site_visit = await db.get(SiteVisit, site_visit_id)

        if not site_visit:
            logger.warning(
                "Site Visit not found",
                extra={"site_visit_id": str(site_visit_id)}
            )
            raise HTTPException(status_code=404, detail="Site Visit not found")

        site_visit_data = SiteVisitRead.model_validate(site_visit).model_dump()

        logger.info(
            "Site Visit retrieved successfully",
            extra={"site_visit_id": str(site_visit_id)}
        )

        return success_response(
            data=site_visit_data,
            message="Site Visit retrieved successfully"
        )

    except HTTPException:
        # Re-raise FastAPI expected errors
        raise

    except Exception as e:
        logger.error(
            f"Failed to get site visit: {str(e)}",
            extra={"site_visit_id": str(site_visit_id)}
        )
        raise HTTPException(status_code=500, detail="Internal server error")

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
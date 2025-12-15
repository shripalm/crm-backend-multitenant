from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.repositories.report_repository import ReportRepository
from app.schemas.report_schemas import ActivityCountsResponse
from app.services.report_service import ReportService
from app.utils.response import StandardResponse
from app.utils.logging import logger


router = APIRouter()


@router.get("/counts", response_model=StandardResponse[ActivityCountsResponse])
async def get_activity_counts(
    user_id: Optional[str] = Query(None, description="Filter by specific user ID"),
    agent_name: Optional[str] = Query(None, description="Filter by agent name (not implemented yet)"),
    project_id: Optional[str] = Query(None, description="Filter by project ID (not supported)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get simple activity counts for dashboard:
    - Scheduled site visits (from leads table where site_visit=true)
    - Total site visits (from site_visits table)  
    - Total tasks (from tasks table)
    - Total offline calls (from call_reports table)
    
    Note: Only user_id filtering is currently supported.
    """
    try:
        service = ReportService(db)
        result = await service.get_activity_counts(
            user_id=user_id,
            agent_name=agent_name,
            project_id=project_id
        )
        return result
        
    except Exception as e:
        logger.error("Error getting activity counts", error=str(e))
        return StandardResponse(
            status="500",
            message="Failed to get activity counts",
            data={
                "scheduled_site_visits": 0,
                "total_site_visits": 0,
                "total_tasks": 0,
                "total_offline_calls": 0
            }
        )

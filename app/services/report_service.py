from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.repositories.report_repository import ReportRepository
from app.schemas.report_schemas import ActivityCounts, ActivityCountsResponse
from app.utils.response import success_response, error_response
from app.utils.logging import logger


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReportRepository(db)

    async def get_activity_counts(
        self,
        user_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """Get activity counts for dashboard"""
        try:
            logger.info(f"Getting activity counts for user_id={user_id}")
            
            counts = await self.repository.get_activity_counts(
                user_id=user_id,
                agent_name=agent_name,  # Note: agent_name filtering not implemented yet
                project_id=project_id
            )
            
            response = ActivityCountsResponse(
                scheduled_site_visits=counts.scheduled_site_visits,
                total_site_visits=counts.total_site_visits,
                total_tasks=counts.total_tasks,
                total_offline_calls=counts.total_offline_calls
            )
            
            return success_response(
                data=response.dict(),
                message="Activity counts retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error getting activity counts: {str(e)}")
            return error_response(
                status_code=500,
                message="Failed to get activity counts"
            )

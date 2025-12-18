from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict, List, Any
from app.schemas.report_schemas import ActivitySummary, UserActivityMetrics, OfflineMetrics, IVRMetrics, ActivityCounts
from app.utils.logging import logger


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_activity_counts(
        self,
        user_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> ActivityCounts:
        """Get simple counts for scheduled site visits, total site visits, and total tasks."""

        try:
            # Build queries conditionally based on parameters
            queries = []
            params = {}

            # Scheduled site visits from leads table
            scheduled_visits_query = "SELECT COUNT(*) FROM leads l"
            if user_id:
                scheduled_visits_query += " WHERE l.employee_id = :user_id"
                params["user_id"] = user_id
            queries.append(f"({scheduled_visits_query}) as scheduled_site_visits")

            # Total site visits from site_visits table
            site_visits_query = "SELECT COUNT(*) FROM site_visits sv"
            if user_id:
                site_visits_query += " WHERE sv.employee_id = :user_id"
            queries.append(f"({site_visits_query}) as total_site_visits")

            # Total tasks from tasks table
            tasks_query = "SELECT COUNT(*) FROM tasks t"
            if user_id:
                tasks_query += " WHERE t.assigned_to = :user_id"
            queries.append(f"({tasks_query}) as total_tasks")

            # Total offline calls from call_reports table
            offline_calls_query = "SELECT COUNT(*) FROM call_reports cr"
            if user_id:
                offline_calls_query += " WHERE cr.employee_id = :user_id"
            queries.append(f"({offline_calls_query}) as total_offline_calls")

            # Note: project_id filtering not implemented as tables don't have project_id columns
            if project_id:
                logger.warning(f"project_id filtering not supported - tables don't have project_id columns")

            # Build final query
            counts_query = f"SELECT {', '.join(queries)}"

            result = await self.db.execute(text(counts_query), params)
            row = result.first()

            if row:
                return ActivityCounts(
                    scheduled_site_visits=row.scheduled_site_visits or 0,
                    total_site_visits=row.total_site_visits or 0,
                    total_tasks=row.total_tasks or 0,
                    total_offline_calls=row.total_offline_calls or 0
                )
            else:
                return ActivityCounts()

        except Exception as e:
            logger.error(f"Error in get_activity_counts: {str(e)}")
            # Return empty counts on error
            return ActivityCounts()

    async def get_activity_report(
        self,
        user_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> tuple[ActivitySummary, List[UserActivityMetrics]]:
        """Get activity report summary and user metrics."""

        # Build WHERE conditions
        conditions = []
        params = {}

        if user_id:
            conditions.append("u.id = :user_id")
            params["user_id"] = user_id

        if agent_name:
            conditions.append("LOWER(u.name) LIKE LOWER(:agent_name)")
            params["agent_name"] = f"%{agent_name}%"

        if project_id:
            conditions.append("""
                (t.project_id = :project_id OR
                 sv.project_id = :project_id OR
                 cr.project_id = :project_id)
            """)
            params["project_id"] = project_id

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Get summary data
        summary_query = f"""
        SELECT
            -- Task counts
            COALESCE(SUM(CASE WHEN t.type != 'meeting' THEN 1 ELSE 0 END), 0) as tasks,
            COALESCE(SUM(CASE WHEN t.type = 'meeting' THEN 1 ELSE 0 END), 0) as meetings,

            -- Site visit counts
            COALESCE(SUM(CASE WHEN sv.status = 'scheduled' THEN 1 ELSE 0 END), 0) as site_visit_scheduled,
            COALESCE(SUM(CASE WHEN sv.status = 'completed' THEN 1 ELSE 0 END), 0) as site_visit_completed,

            -- Offline call metrics
            COALESCE(SUM(cr.offline_lead), 0) as offline_lead,
            COALESCE(SUM(cr.offline_contact), 0) as offline_contact,
            COALESCE(SUM(cr.offline_partner), 0) as offline_channel_partner,

            -- IVR call metrics
            COALESCE(SUM(cr.ivr_lead), 0) as ivr_lead,
            COALESCE(SUM(cr.ivr_contact), 0) as ivr_contact,
            COALESCE(SUM(cr.ivr_partner), 0) as ivr_channel_partner

        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        LEFT JOIN site_visits sv ON u.id = sv.user_id
        LEFT JOIN call_reports cr ON u.id = cr.user_id
        WHERE {where_clause}
        """

        result = await self.db.execute(text(summary_query), params)
        row = result.first()

        if row:
            offline = OfflineMetrics(
                lead=row.offline_lead,
                contact=row.offline_contact,
                channel_partner=row.offline_channel_partner
            )
            ivr = IVRMetrics(
                lead=row.ivr_lead,
                contact=row.ivr_contact,
                channel_partner=row.ivr_channel_partner
            )

            summary = ActivitySummary(
                tasks=row.tasks,
                meetings=row.meetings,
                site_visit_scheduled=row.site_visit_scheduled,
                site_visit_completed=row.site_visit_completed,
                offline=offline,
                total_offline_calls=offline.lead + offline.contact + offline.channel_partner,
                ivr=ivr,
                total_ivr_calls=ivr.lead + ivr.contact + ivr.channel_partner
            )
        else:
            summary = ActivitySummary()

        # Get user metrics
        user_metrics_query = f"""
        SELECT
            u.id as user_id,
            u.name as agent,

            -- Task counts per user
            COALESCE(SUM(CASE WHEN t.type != 'meeting' THEN 1 ELSE 0 END), 0) as tasks,
            COALESCE(SUM(CASE WHEN t.type = 'meeting' THEN 1 ELSE 0 END), 0) as meetings,

            -- Site visit counts per user
            COALESCE(SUM(CASE WHEN sv.status = 'scheduled' THEN 1 ELSE 0 END), 0) as site_visit_scheduled,
            COALESCE(SUM(CASE WHEN sv.status = 'completed' THEN 1 ELSE 0 END), 0) as site_visit_completed,

            -- Offline call metrics per user
            COALESCE(SUM(cr.offline_lead), 0) as offline_lead,
            COALESCE(SUM(cr.offline_contact), 0) as offline_contact,
            COALESCE(SUM(cr.offline_partner), 0) as offline_channel_partner,

            -- IVR call metrics per user
            COALESCE(SUM(cr.ivr_lead), 0) as ivr_lead,
            COALESCE(SUM(cr.ivr_contact), 0) as ivr_contact,
            COALESCE(SUM(cr.ivr_partner), 0) as ivr_partner

        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        LEFT JOIN site_visits sv ON u.id = sv.user_id
        LEFT JOIN call_reports cr ON u.id = cr.user_id
        WHERE {where_clause}
        GROUP BY u.id, u.name
        ORDER BY u.name
        """

        result = await self.db.execute(text(user_metrics_query), params)
        rows = result.fetchall()

        user_metrics = []
        for row in rows:
            offline = OfflineMetrics(
                lead=row.offline_lead,
                contact=row.offline_contact,
                channel_partner=row.offline_channel_partner
            )
            ivr = IVRMetrics(
                lead=row.ivr_lead,
                contact=row.ivr_contact,
                channel_partner=row.ivr_partner
            )

            user_metric = UserActivityMetrics(
                agent=row.agent,
                user_id=str(row.user_id),
                tasks=row.tasks,
                meetings=row.meetings,
                site_visit_scheduled=row.site_visit_scheduled,
                site_visit_completed=row.site_visit_completed,
                offline=offline,
                ivr=ivr
            )
            user_metrics.append(user_metric)

        return summary, user_metrics

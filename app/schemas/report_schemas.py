from pydantic import BaseModel
from typing import Optional, List


class ActivityCounts(BaseModel):
    """Simple activity counts for dashboard"""
    scheduled_site_visits: int = 0
    total_site_visits: int = 0
    total_tasks: int = 0
    total_offline_calls: int = 0


class OfflineMetrics(BaseModel):
    lead: int = 0
    contact: int = 0
    channel_partner: int = 0


class IVRMetrics(BaseModel):
    lead: int = 0
    contact: int = 0
    channel_partner: int = 0


class ActivitySummary(BaseModel):
    tasks: int = 0
    meetings: int = 0
    site_visit_scheduled: int = 0
    site_visit_completed: int = 0
    offline: OfflineMetrics = OfflineMetrics()
    total_offline_calls: int = 0
    ivr: IVRMetrics = IVRMetrics()
    total_ivr_calls: int = 0


class UserActivityMetrics(BaseModel):
    agent: str
    user_id: str
    tasks: int = 0
    meetings: int = 0
    site_visit_scheduled: int = 0
    site_visit_completed: int = 0
    offline: OfflineMetrics = OfflineMetrics()
    ivr: IVRMetrics = IVRMetrics()


class ActivityReportResponse(BaseModel):
    summary: ActivitySummary
    user_metrics: List[UserActivityMetrics]


class ActivityReportFilters(BaseModel):
    user_id: Optional[str] = None
    agent_name: Optional[str] = None
    project_id: Optional[str] = None


class ActivityCountsResponse(BaseModel):
    """Response for activity counts API"""
    scheduled_site_visits: int
    total_site_visits: int
    total_tasks: int
    total_offline_calls: int

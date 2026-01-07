from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class UserCallStats(BaseModel):
    employee_id: Optional[UUID] = None
    full_name: Optional[str] = None
    total_calls: int
    avg_call_duration_seconds: float
    daily_counts: Dict[date, int] = {}


class CallReportStatsData(BaseModel):
    total_calls: int
    total_users: int
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    users: List[UserCallStats]

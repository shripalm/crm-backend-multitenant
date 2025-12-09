from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SiteVisitBase(BaseModel):
    employee_id: Optional[UUID] = Field(None, description="User assigned to this visit")
    contact_id: Optional[UUID] = Field(None, description="Related contact")
    visit_frequency: Optional[str] = Field(
        None, max_length=50, description="Frequency of the visit (e.g., Weekly, Monthly)"
    )
    schedule_date: Optional[datetime] = Field(
        None, description="Scheduled date and time for the visit"
    )
    remark: Optional[str] = Field(None, description="Remarks for this visit")
    lead_id: Optional[UUID] = Field(None, description="Related lead ID, if any")
    last_visited_date: Optional[datetime] = Field(
        None, description="Last date and time when the site was visited"
    )


class SiteVisitCreate(SiteVisitBase):
    """Schema for creating a new SiteVisit"""


class SiteVisitUpdate(BaseModel):
    """Schema for updating an existing SiteVisit"""

    employee_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    visit_frequency: Optional[str] = Field(None, max_length=50)
    schedule_date: Optional[datetime] = None
    remark: Optional[str] = None
    lead_id: Optional[UUID] = None
    last_visited_date: Optional[datetime] = None


class SiteVisitRead(SiteVisitBase):
    """Schema for reading SiteVisit data"""

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


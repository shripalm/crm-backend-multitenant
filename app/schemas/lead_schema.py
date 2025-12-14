from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeadBase(BaseModel):
    contact_id: Optional[UUID] = None
    sales_task_id: Optional[UUID] = None
    remark: Optional[str] = None
    site_visit: bool = False
    last_activity_at: Optional[datetime] = None
    call_duration: Optional[int] = None
    employee_id: Optional[UUID] = None


class LeadCreate(LeadBase):
    assigned_at: Optional[datetime] = None


class LeadUpdate(BaseModel):
    assigned_at: Optional[datetime] = None
    contact_id: Optional[UUID] = None
    sales_task_id: Optional[UUID] = None
    remark: Optional[str] = None
    site_visit: Optional[bool] = None
    last_activity_at: Optional[datetime] = None
    call_duration: Optional[int] = None
    employee_id: Optional[UUID] = None


class LeadRead(LeadBase):
    id: UUID
    created_at: datetime
    assigned_at: Optional[datetime] = None

    class Config:
        from_attributes = True

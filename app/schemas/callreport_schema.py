from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CallReportBase(BaseModel):
    contact_id: UUID = Field(..., description="Reference to contact ID")
    tags: Optional[str] = Field(None, max_length=255, description="Tags (e.g., Hot Lead, Follow-up)")
    sales_agent: Optional[str] = Field(None, max_length=255, description="Assigned sales agent name")
    assigned_date: Optional[datetime] = Field(None, description="Date when lead was assigned")
    last_activity_date: Optional[datetime] = Field(None, description="Last interaction date")
    remark: Optional[str] = Field(None, description="Notes about last activity")
    status: Optional[str] = Field(None, max_length=100, description="Status (e.g., New, In Progress, Closed)")
    source: Optional[str] = Field(None, max_length=100, description="Lead source (e.g., Website, Referral)")
    employee_id: Optional[str] = Field(None, max_length=50, description="Employee identifier")
    call_duration: Optional[int] = Field(None, ge=0, description="Call duration in seconds")
    next_follow_up: Optional[datetime] = Field(None, description="Next scheduled follow-up date")


class CallReportCreate(CallReportBase):
    """Schema for creating a new call report"""
    pass


class CallReportUpdate(BaseModel):
    """Schema for updating an existing call report"""
    contact_id: Optional[UUID] = None
    tags: Optional[str] = Field(None, max_length=255)
    sales_agent: Optional[str] = Field(None, max_length=255)
    assigned_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    remark: Optional[str] = None
    status: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=100)
    employee_id: Optional[str] = Field(None, max_length=50)
    call_duration: Optional[int] = Field(None, ge=0)
    next_follow_up: Optional[datetime] = None


class CallReportRead(CallReportBase):
    """Schema for reading call report data"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

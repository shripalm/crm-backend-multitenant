from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    lead_id: Optional[UUID] = Field(None, description="Reference to lead/contact ID")
    status: Optional[str] = Field(None, max_length=100, description="Task status (e.g., Pending, In Progress, Completed)")
    assigned_to: Optional[str] = Field(None, max_length=255, description="User/Employee name assigned to this task")
    assigned_to_team: Optional[str] = Field(None, max_length=255, description="Team name assigned to this task")
    remarks: Optional[str] = Field(None, description="Detailed notes/comments about the task")
    callback_time: Optional[datetime] = Field(None, description="Scheduled callback date/time")


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""
    lead_id: Optional[UUID] = None
    status: Optional[str] = Field(None, max_length=100)
    assigned_to: Optional[str] = Field(None, max_length=255)
    assigned_to_team: Optional[str] = Field(None, max_length=255)
    remarks: Optional[str] = None
    callback_time: Optional[datetime] = None


class TaskRead(TaskBase):
    """Schema for reading task data"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

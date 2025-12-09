from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class TaskBase(BaseModel):
    lead_id: Optional[UUID] = Field(None, description="Reference to lead/contact ID")
    status: Optional[str] = Field(None, max_length=100, description="Task status (e.g., Pending, In Progress, Completed)")
    assigned_to: Optional[UUID] = Field(None, description="User ID assigned to this task")  # <-- changed to UUID
    assigned_to_team: Optional[str] = Field(None, max_length=255, description="Team name assigned to this task")
    remarks: Optional[str] = Field(None, description="Detailed notes/comments about the task")
    callback_time: Optional[datetime] = Field(None, description="Scheduled callback date/time")


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""
    status: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None
    callback_time: Optional[datetime] = None
    additional_data: Optional[dict] = None  # For any extra fields needed during updates

    # example

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "interested",
                "remarks": "string",
                "callback_time": "2025-12-09T21:48:13.823Z",
                "additional_data": {
                    "tags": "new, hot"
                }
            }
        }
    )


class TaskRead(TaskBase):
    """Schema for reading task data"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

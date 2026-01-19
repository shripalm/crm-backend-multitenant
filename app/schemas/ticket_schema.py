from uuid import UUID
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class TicketBase(BaseModel):
    category: str = Field(..., max_length=100, description="Ticket category: SYSTEM or GENERAL")
    agent_id: Optional[UUID] = Field(
        None,
        description="Agent company ID (for GENERAL tickets)",
    )
    raised_by: UUID = Field(..., description="ID of the user/agent who raised the ticket")

    title: str = Field(..., max_length=255, description="Short title of the ticket")
    description: Optional[str] = Field(None, description="Detailed description of the issue")

    priority: str = Field(..., max_length=50, description="Priority level, e.g. LOW, MEDIUM, HIGH")
    status: str = Field(..., max_length=50, description="Status, e.g. OPEN, IN_PROGRESS, RESOLVED")

    attachment_urls: Optional[List[str]] = Field(
        default=None,
        description="List of attachment URLs related to the ticket",
    )


class TicketCreate(TicketBase):
    """Schema for creating a new ticket"""
    pass


class TicketUpdate(BaseModel):
    """Schema for updating an existing ticket"""

    category: Optional[str] = Field(None, max_length=100)
    agent_id: Optional[UUID] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    attachment_urls: Optional[List[str]] = None
    resolved_at: Optional[datetime] = None


class TicketRead(TicketBase):
    """Schema for reading ticket data"""

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentTicketCreate(BaseModel):
    Agent_Name: str = Field(..., alias="Agent_Name", description="Agent display name")
    Category: str = Field(..., alias="Category")
    priority: str = Field(..., alias="priority")
    Title: str = Field(..., alias="Title")
    Detailed_Description: Optional[str] = Field(None, alias="Detailed Description")
    Attachment: Optional[List[str]] = Field(default=None, alias="Attachment")

    class Config:
        populate_by_name = True


class TicketStatusUpdate(BaseModel):
    status: str
    comment: Optional[str] = None
    user_id: UUID
    user_role: str = Field(..., description="SUPER_ADMIN | AGENT | USER")


class AgentTicketRead(BaseModel):
    Ticket_ID: str = Field(..., alias="Ticket_ID")
    Employee: str = Field(..., alias="Employee")
    Category: str = Field(..., alias="Category")
    Priority: str = Field(..., alias="Priority")
    Title: str = Field(..., alias="Title")
    Description: Optional[str] = Field(None, alias="Description")
    Submitted_on: str = Field(..., alias="Submitted on")
    Status: str = Field(..., alias="Status")
    Activity: Optional[str] = Field(None, alias="Activity")

    class Config:
        populate_by_name = True


class UserTicketCreate(BaseModel):
    Category: str = Field(..., alias="Category")
    priority: str = Field(..., alias="priority")
    Title: str = Field(..., alias="Title")
    Detailed_Description: Optional[str] = Field(None, alias="Detailed Description")
    Attachment: Optional[List[str]] = Field(default=None, alias="Attachment")

    class Config:
        populate_by_name = True

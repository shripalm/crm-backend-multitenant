from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketCommentBase(BaseModel):
    ticket_id: UUID = Field(..., description="Associated ticket ID")
    user_id: UUID = Field(..., description="ID of the user/agent/admin who commented")
    user_role: str = Field(..., max_length=50, description="SUPER_ADMIN | AGENT | USER")
    comment: str = Field(..., description="Comment text")


class TicketCommentCreate(TicketCommentBase):
    """Schema for creating a new ticket comment"""
    pass


class TicketCommentRead(TicketCommentBase):
    """Schema for reading ticket comment data"""

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

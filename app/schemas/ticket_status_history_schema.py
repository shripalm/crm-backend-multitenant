from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketStatusHistoryRead(BaseModel):
    id: UUID
    ticket_id: UUID
    old_status: Optional[str] = None
    new_status: str
    changed_by_id: Optional[UUID] = None
    changed_by_type: Optional[str] = Field(None)
    created_at: datetime

    class Config:
        from_attributes = True

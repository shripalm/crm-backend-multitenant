from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BillingRecordRead(BaseModel):
    id: UUID
    agent_id: UUID
    agent_name: str = Field(..., description="Name of the agent")
    billing_month: date
    active_users: int = Field(..., ge=0)
    price_per_user: float = Field(..., ge=0)
    total_amount: float = Field(..., ge=0)
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

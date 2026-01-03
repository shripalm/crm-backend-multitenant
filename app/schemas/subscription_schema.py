from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionPlanBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price_per_user_monthly: float = Field(..., gt=0)
    is_active: bool = True


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price_per_user_monthly: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class SubscriptionPlanRead(SubscriptionPlanBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentSubscriptionBase(BaseModel):
    agent_id: UUID
    plan_id: UUID
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True


class AgentSubscriptionCreate(AgentSubscriptionBase):
    pass


class AgentSubscriptionUpdate(BaseModel):
    plan_id: Optional[UUID] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class AgentSubscriptionRead(AgentSubscriptionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserActivityLogBase(BaseModel):
    agent_id: UUID
    user_id: UUID
    login_time: datetime


class UserActivityLogCreate(UserActivityLogBase):
    pass


class UserActivityLogRead(UserActivityLogBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

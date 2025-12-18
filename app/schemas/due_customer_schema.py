from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DueCustomerBase(BaseModel):
    last_follow_up_date: Optional[datetime] = Field(
        None, description="Date and time of the last follow-up"
    )
    next_follow_up_date: Optional[datetime] = Field(
        None, description="Date and time of the next scheduled follow-up"
    )
    status: Optional[str] = Field(None, description="Status of the due customer")


class DueCustomerCreate(DueCustomerBase):
    booking_id: UUID = Field(..., description="Booking ID this due customer belongs to")


class DueCustomerUpdate(BaseModel):
    last_follow_up_date: Optional[datetime] = None
    next_follow_up_date: Optional[datetime] = None
    status: Optional[str] = None


class DueCustomerRead(DueCustomerBase):
    booking_id: UUID

    class Config:
        from_attributes = True

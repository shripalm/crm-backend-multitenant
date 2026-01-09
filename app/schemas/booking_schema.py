from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BookingBase(BaseModel):
    booking_date: Optional[datetime] = Field(None, description="Date and time of the booking")
    payment_status: Optional[str] = Field(None, max_length=50, description="Status of the payment")
    payment_paid: Optional[str] = Field(None, max_length=50, description="Amount paid")
    due_date: Optional[datetime] = Field(None, description="Payment due date")
    payment_mode: Optional[str] = Field(None, max_length=50, description="Mode of payment")
    last_follow_up: Optional[datetime] = Field(None, description="Date and time of the last follow-up")
    stage: Optional[str] = Field(None, max_length=50, description="Current stage of the booking process")

    site_visit_id: Optional[UUID] = Field(None, description="ID of the associated site visit")
    core_team_id: Optional[UUID] = Field(None, description="ID of the associated core team member")
    project_id: Optional[UUID] = Field(None, description="ID of the associated project")
    property_id: Optional[UUID] = Field(None, description="ID of the associated property")


class BookingCreate(BookingBase):
    """Schema for creating a new Booking"""


class BookingUpdate(BaseModel):
    """Schema for updating an existing Booking"""

    booking_date: Optional[datetime] = None
    payment_status: Optional[str] = Field(None, max_length=50)
    payment_paid: Optional[str] = Field(None, max_length=50)
    due_date: Optional[datetime] = None
    payment_mode: Optional[str] = Field(None, max_length=50)
    last_follow_up: Optional[datetime] = None
    stage: Optional[str] = Field(None, max_length=50)
    site_visit_id: Optional[UUID] = None
    core_team_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    property_id: Optional[UUID] = None


class BookingRead(BookingBase):
    """Schema for reading Booking data"""

    booking_id: UUID

    class Config:
        from_attributes = True

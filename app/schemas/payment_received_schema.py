from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PaymentReceivedBase(BaseModel):
    booking_id: Optional[UUID] = Field(
        None, description="ID of the associated booking"
    )
    receipt: Optional[str] = Field(
        None,
        max_length=512,
        description="URL of the stored payment receipt",
    )
    stage: Optional[str] = Field(
        None,
        max_length=50,
        description="Current stage of the payment process",
    )


class PaymentReceivedCreate(PaymentReceivedBase):
    """Schema for creating a new payment receipt entry"""

    pass


class PaymentReceivedUpdate(BaseModel):
    """Schema for updating an existing payment receipt entry"""

    booking_id: Optional[UUID] = None
    receipt: Optional[str] = Field(None, max_length=512)
    stage: Optional[str] = Field(None, max_length=50)


class PaymentReceivedRead(PaymentReceivedBase):
    """Schema for reading payment receipt data"""

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

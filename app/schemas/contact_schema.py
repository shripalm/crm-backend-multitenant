from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Contact name")
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    contact_no: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State")
    source: Optional[str] = Field(None, max_length=100, description="Lead source (e.g., Website, Referral)")
    project_name: Optional[str] = Field(None, max_length=255, description="Interested project name")
    property_type: Optional[str] = Field(None, max_length=100, description="Property type (e.g., Apartment, Villa)")
    budget_range: Optional[str] = Field(None, max_length=100, description="Budget range (e.g., 50L-1Cr)")


class ContactCreate(ContactBase):
    """Schema for creating a new contact"""
    pass


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    contact_no: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=100)
    project_name: Optional[str] = Field(None, max_length=255)
    property_type: Optional[str] = Field(None, max_length=100)
    budget_range: Optional[str] = Field(None, max_length=100)


class ContactRead(ContactBase):
    """Schema for reading contact data"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.companyinfo import CompanySizeEnum
from uuid import UUID

class CompanyInfoBase(BaseModel):
    name : Optional[str] = Field(None, max_length=255, description="Company name")
    address : Optional[str] = Field(None, description="Company address")
    phone_number : Optional[str] = Field(None, max_length=20, description="Company phone number")
    email : Optional[EmailStr] = Field(None, max_length=255, description="Company email")
    company_size : CompanySizeEnum 
    description : Optional[str] = Field(None, description="Company description")    

class CompanyInfoCreate(CompanyInfoBase):
    """Schema for creating a new CompanyInfo"""
    pass

class CompanyInfoUpdate(BaseModel):
    """Schema for updating an existing CompanyInfo"""

    name : Optional[str] = Field(None, max_length=255)
    address : Optional[str] = None
    phone_number : Optional[str] = Field(None, max_length=20)
    email : Optional[EmailStr] = Field(None, max_length=255)
    company_size : Optional[CompanySizeEnum] = None
    description : Optional[str] = None  

class CompanyInfoRead(CompanyInfoBase):
    """Schema for reading CompanyInfo data"""

    company_id : UUID

    class Config:
        from_attributes = True
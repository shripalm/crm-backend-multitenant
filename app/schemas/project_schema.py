from __future__ import annotations
from typing import Optional, Dict, Any, List, Union
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
import re

from app.enums.project_enums import ProjectType, ConstructionStatus


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    developer: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    meta: Optional[Dict[str, Any]] = None
    
    # New fields
    project_type: Optional[ProjectType] = None
    address: Optional[str] = Field(None, max_length=1000)
    photo: Optional[str] = Field(None, max_length=500)  # URL or path
    brochure: Optional[str] = Field(None, max_length=500)  # URL or path
    possession_date: Optional[date] = None
    construction_status: Optional[ConstructionStatus] = None
    highlights: Optional[str] = Field(None, max_length=2000)
    total_towers: Optional[Decimal] = Field(None, ge=0)
    no_of_floors: Optional[Decimal] = Field(None, ge=0)
    no_of_units: Optional[Decimal] = Field(None, ge=0)
    flats_per_floor: Optional[Decimal] = Field(None, ge=0)
    lifts_per_floor: Optional[Decimal] = Field(None, ge=0)
    parking_types: Optional[str] = Field(None, max_length=500)
    starting_amount: Optional[Union[int, str]] = Field(None, description="Amount as number (e.g., 20000000) or text format (e.g., '2 cr', '50 lakh')")
    rera_number: Optional[str] = Field(None, max_length=100)
    gst_number: Optional[str] = Field(None, max_length=50)
    consultant: Optional[str] = Field(None, max_length=255)
    architect: Optional[str] = Field(None, max_length=255)
    url_title: Optional[str] = Field(None, max_length=500)
    url_description: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator('starting_amount')
    @classmethod
    def validate_starting_amount(cls, v):
        if v is None:
            return None
        
        # If it's already an integer, convert to Decimal and return
        if isinstance(v, int):
            return Decimal(str(v))
        
        # If it's a string, process text formats
        if isinstance(v, str):
            v = v.strip().lower()
            
            # Handle "cr" format (crore)
            cr_match = re.match(r'^(\d+(?:\.\d+)?)\s*cr$', v)
            if cr_match:
                amount = float(cr_match.group(1)) * 10000000  # 1 crore = 10 million
                return Decimal(str(int(amount)))
            
            # Handle "lakh" format
            lakh_match = re.match(r'^(\d+(?:\.\d+)?)\s*lakh$', v)
            if lakh_match:
                amount = float(lakh_match.group(1)) * 100000  # 1 lakh = 100,000
                return Decimal(str(int(amount)))
            
            # Handle plain number string
            if re.match(r'^\d+$', v):
                return Decimal(v)
            
            raise ValueError(
                "Invalid amount format. Use: "
                "- Numbers: 20000000 "
                "- Crore format: '2 cr' "
                "- Lakh format: '50 lakh'"
            )
        
        raise ValueError("Amount must be an integer or valid text format")


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None

    class Config:
        from_attributes = True


class PropertyBase(BaseModel):
    project_id: Optional[UUID] = None
    unit_number: Optional[str] = None
    size: Optional[float] = None
    price: Optional[float] = None
    status: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyRead(PropertyBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

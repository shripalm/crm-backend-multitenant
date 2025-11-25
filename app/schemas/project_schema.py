from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    developer: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    meta: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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

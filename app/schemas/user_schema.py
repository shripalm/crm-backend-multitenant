from uuid import UUID
from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.role_schema import RoleRead


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    team_name: str | None = None
    agent_id: UUID | None = None
    active: bool = True
    contact: str | None = None
    gender: str | None = None
    address: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=6)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class UserUpdate(BaseModel):
    full_name: str | None = None
    active: bool | None = None
    contact: str | None = None
    gender: str | None = None
    address: str | None = None


class UserRead(UserBase):
    id: UUID
    roles: list[RoleRead] = Field(default_factory=list)
    last_login: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

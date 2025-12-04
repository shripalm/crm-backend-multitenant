from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.role_schema import RoleRead


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    active: bool | None = None


class UserRead(UserBase):
    id: UUID
    roles: list[RoleRead] = Field(default_factory=list)
    last_login: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

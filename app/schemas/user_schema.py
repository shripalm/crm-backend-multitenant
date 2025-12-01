from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.team_schema import TeamOut
from app.schemas.role_schema import RoleOut


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    active: bool = True


class UserCreate(UserBase):
    password: str
    team_id: UUID | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    active: bool | None = None
    team_id: UUID | None = None


class UserOut(UserBase):
    id: UUID
    team: Optional[TeamOut] = None
    roles: list[RoleOut] = Field(default_factory=list)
    last_login: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

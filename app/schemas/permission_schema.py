from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class PermissionBase(BaseModel):
    name: str
    label: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    label: str | None = None
    description: str | None = None


class PermissionRead(PermissionBase):
    id: UUID
    created_at: datetime | None = None

    class Config:
        from_attributes = True

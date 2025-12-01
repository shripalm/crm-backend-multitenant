from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.schemas.permission_schema import PermissionRead


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleRead(RoleBase):
    id: UUID
    created_at: datetime | None = None
    permissions: list[PermissionRead] = []

    class Config:
        from_attributes = True

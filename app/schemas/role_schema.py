from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    user_email: str | None = None  # Optional user email to assign role to


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleRead(RoleBase):
    id: UUID
    created_at: datetime | None = None

    class Config:
        from_attributes = True

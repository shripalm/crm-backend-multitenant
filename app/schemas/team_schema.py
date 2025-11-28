from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str
    description: str | None = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TeamOut(TeamBase):
    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

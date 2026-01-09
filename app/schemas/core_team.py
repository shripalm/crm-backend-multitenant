from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class CoreTeamBase(BaseModel):
    name: str
    number: Optional[str] = None

class CoreTeamCreate(CoreTeamBase):
    id: Optional[UUID] = None

class CoreTeamUpdate(BaseModel):
    name: Optional[str] = None

class CoreTeam(CoreTeamBase):
    id: UUID
    number: Optional[str] = None

    class Config:
        from_attributes = True

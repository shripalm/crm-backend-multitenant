from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID


class PropertyBase(BaseModel):
    unit_number: Optional[str] = None
    size: Optional[float] = None
    price: Optional[float] = None
    status: Optional[str] = None
    attributes: Optional[Dict] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyRead(PropertyBase):
    id: UUID
    project_id: UUID

    
    model_config = {
        "from_attributes": True
    }

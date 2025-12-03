from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class UploadBase(BaseModel):
    filename: str
    file_type: str
    rows_processed: int


class UploadResponse(UploadBase):
    uploaded_at: datetime
    data: List[Dict[str, Any]]

    class Config:
        from_attributes = True

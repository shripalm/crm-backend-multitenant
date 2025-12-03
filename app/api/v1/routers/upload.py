from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.services import upload as upload_service

router = APIRouter()


@router.post("/", response_model=StandardResponse[dict])
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process Excel or CSV file. Router simply returns the service result."""
    # Validate file extension
    if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only .xlsx, .xls, and .csv files are allowed."
        )
    
    # Read file content
    file_content = await file.read()
    
    # Process file through service
    return await upload_service.process_file(db, file_content, file.filename)

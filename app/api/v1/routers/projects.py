from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.schemas.project_schema import ProjectCreate
from app.services import projects as projects_service

router = APIRouter()


@router.post("/", response_model=StandardResponse[dict])
async def add_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project. Router simply returns the service result."""
    return await projects_service.create_project(db, payload)


@router.get("/", response_model=StandardResponse[List[dict]])
async def list_projects(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List projects with pagination. Router simply returns the service result."""
    return await projects_service.list_projects(db, limit=limit, offset=offset)

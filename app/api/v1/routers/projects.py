from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.schemas.project_schema import ProjectCreate, ProjectRead
from app.services import projects as projects_service
from app.utils.logging import logger
from app.utils.pagination import PaginationParams

router = APIRouter()


@router.post(
    "/", 
    response_model=StandardResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new real estate project with all details including type, amenities, and specifications",
    responses={
        201: {"description": "Project created successfully"},
        400: {"description": "Invalid input data"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def add_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project with proper error handling and status codes."""
    try:
        logger.info("Received project creation request", project_name=payload.name)
        
        # Validate required fields
        if not payload.name or payload.name.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "400",
                    "message": "Project name is required",
                    "data": {}
                }
            )
        
        # Call service layer
        result = await projects_service.create_project(db, payload)
        
        logger.info("Project created successfully", project_name=payload.name)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions from service layer or validation
        raise
        
    except SQLAlchemyError as e:
        logger.error("Database error during project creation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "500",
                "message": "Database error occurred while creating project",
                "data": {}
            }
        )
        
    except Exception as e:
        logger.error("Unexpected error during project creation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "500",
                "message": "An unexpected error occurred while creating project",
                "data": {}
            }
        )


@router.get("/", response_model=StandardResponse)
async def list_projects(
    page: int = Query(1, description="Page number (starts from 1)"),
    size: int = Query(20, description="Items per page (max 100)"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction (asc or desc)"),
    db: AsyncSession = Depends(get_db)
):
    """List projects with pagination. Router simply returns the service result."""
    pagination_params = PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_direction=sort_direction.lower() if sort_direction else "desc",
    )
    return await projects_service.list_projects(db, pagination_params)


@router.delete("/{project_id}", response_model=StandardResponse)
async def delete_project_soft(project_id: str, db: AsyncSession = Depends(get_db)):
    return await projects_service.soft_delete_project(db, project_id)

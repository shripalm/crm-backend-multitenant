from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from decimal import Decimal

from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.schemas.incentive_schema import (
    IncentiveConfigCreate,
    IncentiveConfigRead,
    IncentiveCalculationRequest,
    IncentiveCalculationResponse
)
from app.services.incentive_service import (
    get_default_incentive_config,
    set_default_incentive_config,
    get_project_incentive_config,
    create_project_incentive_config,
    calculate_incentive
)
from app.utils.response import success_response, created_response, error_response
from app.utils.logging import logger

router = APIRouter()


@router.post(
    "/default",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set default incentive configuration",
    description="Create or update the global default incentive configuration"
)
async def set_default_config(
    config: IncentiveConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """Set the default incentive configuration."""
    try:
        new_config = await set_default_incentive_config(db, config)
        config_data = IncentiveConfigRead.model_validate(new_config).model_dump()
        return created_response(
            data=config_data,
            message="Default incentive configuration set successfully"
        )
    except Exception as e:
        logger.error(f"Error setting default config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default configuration: {str(e)}"
        )


@router.get(
    "/default",
    response_model=StandardResponse,
    summary="Get default incentive configuration",
    description="Retrieve the global default incentive configuration used for all projects"
)
async def get_default_config(db: AsyncSession = Depends(get_db)):
    """Get the default incentive configuration."""
    try:
        config = await get_default_incentive_config(db)
        config_data = IncentiveConfigRead.model_validate(config).model_dump()
        return success_response(
            data=config_data,
            message="Default incentive configuration retrieved successfully"
        )
    except ValueError as ve:
        return error_response(404, str(ve))
    except Exception as e:
        logger.error(f"Error retrieving default config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve default configuration: {str(e)}"
        )


@router.get(
    "/config/{project_id}",
    response_model=StandardResponse,
    summary="Get project incentive configuration",
    description="Retrieve the incentive configuration for a specific project"
)
async def get_project_config(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get incentive configuration for a specific project."""
    try:
        config = await get_project_incentive_config(db, project_id)
        if not config:
            return error_response(404, f"No incentive configuration found for project {project_id}")
        
        config_data = IncentiveConfigRead.model_validate(config).model_dump()
        return success_response(
            data=config_data,
            message="Project incentive configuration retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving project config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project configuration: {str(e)}"
        )


@router.post(
    "/config",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project incentive configuration",
    description="Create or update a project-specific incentive configuration"
)
async def create_config(
    project_id: UUID = Body(..., description="Project ID for the configuration"),
    config: IncentiveConfigCreate = Body(..., description="Incentive configuration details"),
    db: AsyncSession = Depends(get_db)
):
    """Create a project-specific incentive configuration."""
    try:
        new_config = await create_project_incentive_config(db, project_id, config)
        config_data = IncentiveConfigRead.model_validate(new_config).model_dump()
        return created_response(
            data=config_data,
            message="Project incentive configuration created successfully"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error creating project config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project configuration: {str(e)}"
        )


@router.post(
    "/calculate",
    response_model=StandardResponse,
    summary="Calculate incentive",
    description="Calculate incentive based on calculation type and metrics"
)
async def calculate_incentive_endpoint(
    request: IncentiveCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate incentive based on calculation type and metrics."""
    try:
        calculation = await calculate_incentive(
            db,
            project_id=request.project_id,
            calculation_type=request.calculation_type,
            calls_made=request.calls_made,
            deal_amount=request.deal_amount
        )
        
        return success_response(
            data=calculation.model_dump(),
            message="Incentive calculated successfully"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error calculating incentive: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate incentive: {str(e)}"
        )

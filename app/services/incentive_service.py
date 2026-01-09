from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from decimal import Decimal

from app.models.incentive_config import IncentiveConfiguration
# Deal model removed - incentive calculation now independent
from app.schemas.incentive_schema import (
    IncentiveConfigCreate,
    IncentiveConfigRead,
    IncentiveCalculationResponse
)
# DealStage enum removed - incentive calculation now independent
from app.utils.logging import logger


async def get_default_incentive_config(db: AsyncSession) -> IncentiveConfiguration:
    """
    Fetch the single default incentive configuration.
    Raises an exception if not found.
    """
    query = select(IncentiveConfiguration).where(IncentiveConfiguration.is_default == True)
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise ValueError("Default incentive configuration not found. Please ensure the system is properly initialized.")
    
    return config


async def set_default_incentive_config(
    db: AsyncSession,
    config_data: IncentiveConfigCreate
) -> IncentiveConfiguration:
    """
    Create or update the global default incentive configuration.
    """
    try:
        # Check if default already exists
        query = select(IncentiveConfiguration).where(IncentiveConfiguration.is_default == True)
        result = await db.execute(query)
        config = result.scalar_one_or_none()
        
        config_dict = config_data.model_dump()
        
        if config:
            # Update existing default
            for key, value in config_dict.items():
                setattr(config, key, value)
            logger.info("Updated global default incentive configuration")
        else:
            # Create new default
            config = IncentiveConfiguration(
                is_default=True,
                project_id=None,
                **config_dict
            )
            db.add(config)
            logger.info("Created new global default incentive configuration")
            
        await db.commit()
        await db.refresh(config)
        return config
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error setting default incentive config: {str(e)}")
        raise


async def get_project_incentive_config(db: AsyncSession, project_id: UUID) -> Optional[IncentiveConfiguration]:
    """
    Get incentive configuration for a specific project.
    Returns None if not found.
    """
    query = select(IncentiveConfiguration).where(
        IncentiveConfiguration.project_id == project_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_project_incentive_config(
    db: AsyncSession,
    project_id: UUID,
    config_data: IncentiveConfigCreate
) -> IncentiveConfiguration:
    """
    Create a project-specific incentive configuration.
    Validates that no duplicate configuration exists for the same project.
    """
    try:
        # Check if config already exists for this project
        existing = await get_project_incentive_config(db, project_id)
        if existing:
            raise ValueError(f"Incentive configuration already exists for project {project_id}")
        
        # Create new configuration
        config_dict = config_data.model_dump()
        config = IncentiveConfiguration(
            is_default=False,
            project_id=project_id,
            **config_dict
        )
        
        db.add(config)
        await db.commit()
        await db.refresh(config)
        
        logger.info("Created project-specific incentive config", project_id=str(project_id))
        return config
        
    except IntegrityError as e:
        await db.rollback()
        logger.error("Database integrity error creating incentive config", error=str(e))
        raise ValueError(f"Failed to create incentive configuration: {str(e)}")


async def copy_default_to_project(db: AsyncSession, project_id: UUID) -> IncentiveConfiguration:
    """
    Copy the default incentive configuration to a specific project.
    Used when "Skip Incentives for Now" is selected.
    Ensures every project has an explicit configuration.
    """
    try:
        # Get default config
        default_config = await get_default_incentive_config(db)
        
        # Check if config already exists for this project
        existing = await get_project_incentive_config(db, project_id)
        if existing:
            logger.warning("Project already has incentive config, skipping copy", project_id=str(project_id))
            return existing
        
        # Create project-specific config with default values
        project_config = IncentiveConfiguration(
            is_default=False,
            project_id=project_id,
            presales_calls_per_unit=default_config.presales_calls_per_unit,
            presales_incentive_amount=default_config.presales_incentive_amount,
            sales_calls_per_unit=default_config.sales_calls_per_unit,
            sales_incentive_amount=default_config.sales_incentive_amount,
            site_visit_percentage=default_config.site_visit_percentage,
            core_team_percentage=default_config.core_team_percentage
        )
        
        db.add(project_config)
        await db.commit()
        await db.refresh(project_config)
        
        logger.info("Copied default incentive config to project", project_id=str(project_id))
        return project_config
        
    except Exception as e:
        await db.rollback()
        logger.error("Failed to copy default config to project", project_id=str(project_id), error=str(e))
        raise


async def calculate_incentive(
    db: AsyncSession,
    project_id: Optional[UUID] = None,
    calculation_type: str = "fixed",  # "fixed" or "percentage"
    calls_made: Optional[int] = None,
    deal_amount: Optional[Decimal] = None
) -> IncentiveCalculationResponse:
    """
    Calculate incentive based on configuration and calculation type.
    
    For "fixed" type: Uses fixed formula based on calls
    For "percentage" type: Uses percentage of deal_amount
    
    Returns calculation breakdown with detailed explanation.
    """
    # Get the appropriate incentive configuration
    if project_id:
        config = await get_project_incentive_config(db, project_id)
        if not config:
            # Fallback to default if project config doesn't exist
            config = await get_default_incentive_config(db)
    else:
        config = await get_default_incentive_config(db)
    
    # Calculate based on type
    if calculation_type == "fixed":
        # Fixed incentive calculation (call-based)
        if calls_made is None:
            raise ValueError("calls_made is required for fixed calculation type")
        
        calls_per_unit = config.presales_calls_per_unit
        incentive_per_unit = config.presales_incentive_amount
        
        units_earned = Decimal(calls_made) / Decimal(calls_per_unit)
        incentive_amount = units_earned * incentive_per_unit
        
        breakdown = {
            "type": "fixed",
            "calls_made": calls_made,
            "calls_per_unit": calls_per_unit,
            "incentive_per_unit": float(incentive_per_unit),
            "units_earned": float(units_earned),
            "formula": f"({calls_made} / {calls_per_unit}) * {incentive_per_unit} = {incentive_amount}"
        }
        
    elif calculation_type == "percentage":
        # Percentage-based incentive calculation
        if deal_amount is None:
            raise ValueError("deal_amount is required for percentage calculation type")
        
        percentage = config.site_visit_percentage
        
        incentive_amount = (deal_amount * percentage) / Decimal(100)
        
        breakdown = {
            "type": "percentage",
            "deal_amount": float(deal_amount),
            "percentage": float(percentage),
            "formula": f"({deal_amount} * {percentage}%) / 100 = {incentive_amount}"
        }
    else:
        raise ValueError(f"Unknown calculation type: {calculation_type}")
    
    return IncentiveCalculationResponse(
        deal_id=None,  # No longer tied to specific deal
        stage=None,    # No longer using deal stages
        incentive_amount=incentive_amount,
        calculation_breakdown=breakdown
    )


async def validate_default_uniqueness(db: AsyncSession, config_id: Optional[UUID] = None) -> bool:
    """
    Ensure only one is_default=true record exists.
    Used before creating/updating configs.
    
    Args:
        config_id: If provided, exclude this config from the check (for updates)
    
    Returns:
        True if validation passes, False otherwise
    """
    query = select(IncentiveConfiguration).where(IncentiveConfiguration.is_default == True)
    
    if config_id:
        query = query.where(IncentiveConfiguration.id != config_id)
    
    result = await db.execute(query)
    existing_defaults = result.scalars().all()
    
    return len(existing_defaults) <= 1

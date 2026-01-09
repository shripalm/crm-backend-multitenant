from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.project_schema import ProjectCreate
from app.schemas.incentive_schema import IncentiveConfigCreate


class ProjectWithIncentiveCreate(BaseModel):
    """
    Combined schema for creating a project with incentive options.
    This keeps the base ProjectCreate schema clean and separated from incentive logic.
    """
    project_data: ProjectCreate = Field(..., description="Project details")
    
    # Incentive configuration options
    add_incentives: bool = Field(
        default=False,
        description="Whether to add custom incentives or skip for now (will copy default)"
    )
    incentive_config: Optional[IncentiveConfigCreate] = Field(
        default=None,
        description="Custom incentive configuration (required if add_incentives=True)"
    )
    
    @field_validator('incentive_config')
    @classmethod
    def validate_incentive_config(cls, v, info):
        """Validate that incentive_config is provided when add_incentives is True"""
        add_incentives = info.data.get('add_incentives', False)
        if add_incentives and not v:
            raise ValueError("incentive_config is required when add_incentives=True")
        if not add_incentives and v:
            raise ValueError("incentive_config should not be provided when add_incentives=False")
        return v

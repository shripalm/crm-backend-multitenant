from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

# DealStage enum removed - incentive calculation now independent


class IncentiveConfigBase(BaseModel):
    """Base schema for Incentive Configuration"""
    # Fixed incentives for Presales and Sales
    presales_calls_per_unit: int = Field(
        default=1000,
        ge=1,
        description="Number of calls per unit for presales incentive calculation"
    )
    presales_incentive_amount: Decimal = Field(
        default=Decimal("500.00"),
        ge=0,
        description="Incentive amount in rupees for presales per unit"
    )
    
    sales_calls_per_unit: int = Field(
        default=1000,
        ge=1,
        description="Number of calls per unit for sales incentive calculation"
    )
    sales_incentive_amount: Decimal = Field(
        default=Decimal("500.00"),
        ge=0,
        description="Incentive amount in rupees for sales per unit"
    )
    
    # Percentage-based incentives for Site Visit and Core Team
    site_visit_percentage: Decimal = Field(
        default=Decimal("1.5"),
        ge=0,
        le=100,
        description="Incentive percentage for site visit stage (e.g., 1.5 for 1.5%)"
    )
    core_team_percentage: Decimal = Field(
        default=Decimal("2.0"),
        ge=0,
        le=100,
        description="Incentive percentage for core team stage (e.g., 2.0 for 2%)"
    )


class IncentiveConfigCreate(IncentiveConfigBase):
    """Schema for creating incentive configuration"""
    pass


class IncentiveConfigRead(IncentiveConfigBase):
    """Schema for reading incentive configuration"""
    id: UUID
    is_default: bool
    project_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IncentiveCalculationRequest(BaseModel):
    """Schema for requesting incentive calculation"""
    project_id: Optional[UUID] = Field(None, description="Project ID for project-specific config")
    calculation_type: str = Field("fixed", description="Calculation type: 'fixed' or 'percentage'")
    calls_made: Optional[int] = Field(None, ge=0, description="Number of calls made (for fixed calculation)")
    deal_amount: Optional[Decimal] = Field(None, ge=0, description="Deal value (for percentage calculation)")


class IncentiveCalculationResponse(BaseModel):
    """Schema for incentive calculation response"""
    deal_id: Optional[UUID] = None
    stage: Optional[str] = None
    incentive_amount: Decimal
    calculation_breakdown: dict = Field(
        ...,
        description="Detailed breakdown of how incentive was calculated"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "deal_id": "550e8400-e29b-41d4-a716-446655440000",
                "stage": "presales",
                "incentive_amount": 2500.00,
                "calculation_breakdown": {
                    "type": "fixed",
                    "calls_made": 5000,
                    "calls_per_unit": 1000,
                    "incentive_per_unit": 500.00,
                    "units_earned": 5.0,
                    "formula": "(5000 / 1000) * 500.00 = 2500.00"
                }
            }
        }


class ProjectIncentiveConfigInput(BaseModel):
    """Schema for incentive configuration input when creating a project"""
    add_incentives: bool = Field(
        default=False,
        description="Whether to add custom incentives or use default"
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

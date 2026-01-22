from sqlalchemy import Column, Numeric, TIMESTAMP, ForeignKey, Boolean, Integer, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import sqlalchemy as sa

from app.db.base_class import Base


class IncentiveConfiguration(Base):
    __tablename__ = "incentive_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"))
    
    # Configuration type
    is_default = Column(Boolean, nullable=False, default=False)
    
    # Project relationship (NULL for default config)
    project_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("projects.id", ondelete="CASCADE"), 
        nullable=True
    )
    
    # Fixed incentives for Presales and Sales (call-based)
    presales_calls_per_unit = Column(Integer, nullable=False, default=1000)
    presales_incentive_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=500.00)
    
    sales_calls_per_unit = Column(Integer, nullable=False, default=1000)
    sales_incentive_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=500.00)
    
    # Percentage-based incentives for Site Visit and Core Team
    site_visit_percentage = Column(Numeric(precision=5, scale=2), nullable=False, default=1.5)
    core_team_percentage = Column(Numeric(precision=5, scale=2), nullable=False, default=2.0)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    
    # Relationships
    project = relationship("Project")
    
    # Table constraints
    __table_args__ = (
        # Ensure only one default configuration exists
        Index('uq_single_default_config', 'is_default', unique=True, postgresql_where=sa.text('is_default = true')),
        # Ensure one configuration per project
        Index('uq_one_config_per_project', 'project_id', unique=True, postgresql_where=sa.text('project_id IS NOT NULL')),
        # Ensure percentages are positive
        CheckConstraint('site_visit_percentage >= 0 AND site_visit_percentage <= 100', name='check_site_visit_percentage'),
        CheckConstraint('core_team_percentage >= 0 AND core_team_percentage <= 100', name='check_core_team_percentage'),
        # Ensure call units are positive
        CheckConstraint('presales_calls_per_unit > 0', name='check_presales_calls'),
        CheckConstraint('sales_calls_per_unit > 0', name='check_sales_calls'),
        # Ensure incentive amounts are positive
        CheckConstraint('presales_incentive_amount >= 0', name='check_presales_amount'),
        CheckConstraint('sales_incentive_amount >= 0', name='check_sales_amount'),
    )

    def __repr__(self) -> str:
        config_type = "Default" if self.is_default else f"Project {self.project_id}"
        return f"<IncentiveConfiguration {config_type}>"

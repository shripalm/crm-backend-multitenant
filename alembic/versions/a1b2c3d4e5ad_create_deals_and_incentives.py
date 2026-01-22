"""create deals and incentive configurations tables

Revision ID: a1b2c3d4e5ad
Revises: a1b2c3d4e5ac
Create Date: 2026-01-07 09:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5ad"
down_revision = "a1b2c3d4e5ac"
branch_labels = None
depends_on = None


deal_stage_enum = postgresql.ENUM(
    "presales",
    "sales",
    "site_visit",
    "core_team",
    name="deal_stage",
    create_type=False
)


def upgrade() -> None:
    # Ensure uuid-ossp extension for uuid_generate_v4()
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Create deal_stage enum
    deal_stage_enum.create(op.get_bind(), checkfirst=True)

    # Create deals table
    op.create_table(
        "deals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contacts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("deal_name", sa.Text(), nullable=True),
        sa.Column(
            "current_stage",
            deal_stage_enum,
            nullable=False,
            server_default="presales",
        ),
        sa.Column("deal_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("stage_history", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    # Create indexes for deals
    op.create_index("idx_deals_project_id", "deals", ["project_id"])
    op.create_index("idx_deals_contact_id", "deals", ["contact_id"])
    op.create_index("idx_deals_employee_id", "deals", ["employee_id"])
    op.create_index("idx_deals_current_stage", "deals", ["current_stage"])
    op.create_index("idx_deals_created_at", "deals", ["created_at"])

    # Create incentive_configurations table
    op.create_table(
        "incentive_configurations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        # Fixed incentives for Presales and Sales
        sa.Column("presales_calls_per_unit", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column(
            "presales_incentive_amount",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="500.00",
        ),
        sa.Column("sales_calls_per_unit", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column(
            "sales_incentive_amount",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="500.00",
        ),
        # Percentage-based incentives for Site Visit and Core Team
        sa.Column(
            "site_visit_percentage",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default="1.5",
        ),
        sa.Column(
            "core_team_percentage",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default="2.0",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Create unique constraint for single default config
    op.create_index(
        "idx_single_default_config",
        "incentive_configurations",
        ["is_default"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )

    # Create unique constraint for one config per project
    op.create_index(
        "idx_one_config_per_project",
        "incentive_configurations",
        ["project_id"],
        unique=True,
        postgresql_where=sa.text("project_id IS NOT NULL"),
    )

    # Create index for project_id lookups
    op.create_index("idx_incentive_project_id", "incentive_configurations", ["project_id"])

    # Add check constraints for valid percentages and amounts
    op.create_check_constraint(
        "check_site_visit_percentage",
        "incentive_configurations",
        "site_visit_percentage >= 0 AND site_visit_percentage <= 100",
    )
    op.create_check_constraint(
        "check_core_team_percentage",
        "incentive_configurations",
        "core_team_percentage >= 0 AND core_team_percentage <= 100",
    )
    op.create_check_constraint(
        "check_presales_calls", "incentive_configurations", "presales_calls_per_unit > 0"
    )
    op.create_check_constraint(
        "check_sales_calls", "incentive_configurations", "sales_calls_per_unit > 0"
    )
    op.create_check_constraint(
        "check_presales_amount", "incentive_configurations", "presales_incentive_amount >= 0"
    )
    op.create_check_constraint(
        "check_sales_amount", "incentive_configurations", "sales_incentive_amount >= 0"
    )

    # Insert default incentive configuration
    op.execute(
        """
        INSERT INTO incentive_configurations (
            is_default,
            project_id,
            presales_calls_per_unit,
            presales_incentive_amount,
            sales_calls_per_unit,
            sales_incentive_amount,
            site_visit_percentage,
            core_team_percentage
        ) VALUES (
            true,
            NULL,
            1000,
            500.00,
            1000,
            500.00,
            1.5,
            2.0
        );
    """
    )


def downgrade() -> None:
    # Drop tables
    op.drop_index("idx_incentive_project_id", table_name="incentive_configurations")
    op.drop_index(
        "idx_one_config_per_project",
        table_name="incentive_configurations",
        postgresql_where=sa.text("project_id IS NOT NULL"),
    )
    op.drop_index(
        "idx_single_default_config",
        table_name="incentive_configurations",
        postgresql_where=sa.text("is_default = true"),
    )
    op.drop_table("incentive_configurations")

    op.drop_index("idx_deals_created_at", table_name="deals")
    op.drop_index("idx_deals_current_stage", table_name="deals")
    op.drop_index("idx_deals_employee_id", table_name="deals")
    op.drop_index("idx_deals_contact_id", table_name="deals")
    op.drop_index("idx_deals_project_id", table_name="deals")
    op.drop_table("deals")

    # Enum deal_stage is not dropped to support multi-tenant environments where it might be shared
    pass

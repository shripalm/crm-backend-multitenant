"""create subscription tables in admin database

Revision ID: 2345678901c0
Revises: 2345678901bf
Create Date: 2025-12-26 11:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2345678901c0"
down_revision: Union[str, None] = "2345678901bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription_plans",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_per_user_monthly", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "agent_subscriptions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subscription_plans.id"),
            nullable=False,
        ),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_agent_subscriptions_agent_id",
        "agent_subscriptions",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_subscriptions_plan_id",
        "agent_subscriptions",
        ["plan_id"],
        unique=False,
    )

    op.create_table(
        "user_activity_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("login_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_user_activity_logs_agent_id",
        "user_activity_logs",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_activity_logs_user_id",
        "user_activity_logs",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_activity_logs_login_time",
        "user_activity_logs",
        ["login_time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_activity_logs_login_time", table_name="user_activity_logs")
    op.drop_index("ix_user_activity_logs_user_id", table_name="user_activity_logs")
    op.drop_index("ix_user_activity_logs_agent_id", table_name="user_activity_logs")
    op.drop_table("user_activity_logs")

    op.drop_index("ix_agent_subscriptions_plan_id", table_name="agent_subscriptions")
    op.drop_index("ix_agent_subscriptions_agent_id", table_name="agent_subscriptions")
    op.drop_table("agent_subscriptions")

    op.drop_table("subscription_plans")

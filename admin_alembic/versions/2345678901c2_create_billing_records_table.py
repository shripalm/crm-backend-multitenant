"""create billing_records table in admin database

Revision ID: 2345678901c2
Revises: 2345678901c1
Create Date: 2025-12-26 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2345678901c2"
down_revision: Union[str, None] = "2345678901c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "billing_records",
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
        sa.Column("billing_month", sa.Date(), nullable=False),
        sa.Column("active_users", sa.Integer(), nullable=False),
        sa.Column("price_per_user", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("agent_id", "billing_month", name="uq_billing_records_agent_month"),
    )

    op.create_index("ix_billing_records_agent_id", "billing_records", ["agent_id"], unique=False)
    op.create_index("ix_billing_records_billing_month", "billing_records", ["billing_month"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_billing_records_billing_month", table_name="billing_records")
    op.drop_index("ix_billing_records_agent_id", table_name="billing_records")
    op.drop_table("billing_records")

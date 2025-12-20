"""create agent_otps table for password reset OTP

Revision ID: 2345678901be
Revises: 2345678901bd
Create Date: 2025-12-17 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2345678901be"
down_revision: Union[str, None] = "2345678901bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_otps",
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
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("otp_code", sa.String(length=10), nullable=False),
        sa.Column("reset_token", sa.String(length=255), nullable=True),
        sa.Column("is_verified", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_used", sa.Boolean(), default=False, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_agent_otps_agent_id", "agent_otps", ["agent_id"], unique=False)
    op.create_index("ix_agent_otps_email", "agent_otps", ["email"], unique=False)
    op.create_index("ix_agent_otps_reset_token", "agent_otps", ["reset_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_agent_otps_reset_token", table_name="agent_otps")
    op.drop_index("ix_agent_otps_email", table_name="agent_otps")
    op.drop_index("ix_agent_otps_agent_id", table_name="agent_otps")
    op.drop_table("agent_otps")

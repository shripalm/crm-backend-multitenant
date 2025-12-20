"""create admin_otps table for password reset OTP

Revision ID: 2345678901bf
Revises: 2345678901be
Create Date: 2025-12-17 14:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2345678901bf"
down_revision: Union[str, None] = "2345678901be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_otps",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "admin_id",
            sa.Integer(),
            sa.ForeignKey("admin.id", ondelete="CASCADE"),
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
    op.create_index("ix_admin_otps_admin_id", "admin_otps", ["admin_id"], unique=False)
    op.create_index("ix_admin_otps_email", "admin_otps", ["email"], unique=False)
    op.create_index("ix_admin_otps_reset_token", "admin_otps", ["reset_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_admin_otps_reset_token", table_name="admin_otps")
    op.drop_index("ix_admin_otps_email", table_name="admin_otps")
    op.drop_index("ix_admin_otps_admin_id", table_name="admin_otps")
    op.drop_table("admin_otps")

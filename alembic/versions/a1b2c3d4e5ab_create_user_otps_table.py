"""create user_otps table for password reset OTP

Revision ID: a1b2c3d4e5ab
Revises: a1b2c3d4e5aa
Create Date: 2025-12-17 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5ab"
down_revision: Union[str, None] = "a1b2c3d4e5aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_otps",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
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
    op.create_index("ix_user_otps_user_id", "user_otps", ["user_id"], unique=False)
    op.create_index("ix_user_otps_email", "user_otps", ["email"], unique=False)
    op.create_index("ix_user_otps_reset_token", "user_otps", ["reset_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_user_otps_reset_token", table_name="user_otps")
    op.drop_index("ix_user_otps_email", table_name="user_otps")
    op.drop_index("ix_user_otps_user_id", table_name="user_otps")
    op.drop_table("user_otps")

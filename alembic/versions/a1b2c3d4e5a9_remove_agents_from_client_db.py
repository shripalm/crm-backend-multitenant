"""remove agents table from client database

Revision ID: a1b2c3d4e5a9
Revises: a1b2c3d4e5a8
Create Date: 2025-12-12 11:41:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5a9"
down_revision: Union[str, None] = "a1b2c3d4e5a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove agents table from client database.
    Agents are now managed in the admin database.
    """
    # Drop indexes first
    op.drop_index("ix_agents_username", table_name="agents")
    op.drop_index("ix_agents_email", table_name="agents")
    # Drop the table
    op.drop_table("agents")


def downgrade() -> None:
    """
    Recreate agents table in client database if downgrading.
    Note: Data migration from admin DB to client DB is not included.
    """
    op.create_table(
        "agents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("logo_url", sa.String(length=512), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("contact_no", sa.String(length=50), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("experience", sa.String(length=100), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
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
        sa.UniqueConstraint("email", name="uq_agents_email"),
        sa.UniqueConstraint("username", name="uq_agents_username"),
    )
    op.create_index("ix_agents_email", "agents", ["email"], unique=False)
    op.create_index("ix_agents_username", "agents", ["username"], unique=False)

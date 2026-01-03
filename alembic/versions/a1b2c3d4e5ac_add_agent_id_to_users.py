"""add agent_id to users

Revision ID: a1b2c3d4e5ac
Revises: a1b2c3d4e5ab
Create Date: 2025-12-26 12:20:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5ac"
down_revision = "a1b2c3d4e5ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_users_agent_id", "users", ["agent_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_agent_id", table_name="users")
    op.drop_column("users", "agent_id")

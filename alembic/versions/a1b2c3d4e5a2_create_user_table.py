"""create unified schema

Revision ID: a1b2c3d4e5a2
Revises: a1b2c3d4e5a1
Create Date: 2025-08-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5a2'
down_revision = 'a1b2c3d4e5a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
        # ROLES TABLE REMOVED

    # users
    # Note: `okta_verification` was unspecified in the source; choose Boolean to represent verification state.

  

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("team_name", sa.String(255), nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('users')
   
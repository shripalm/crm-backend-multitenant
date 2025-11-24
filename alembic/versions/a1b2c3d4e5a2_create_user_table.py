"""create unified schema

Revision ID: a1b2c3d4e5a2
Revises: a1b2c3d4e5a1
Create Date: 2025-08-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

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
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(length=64), nullable=False, unique=True),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('last_login', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_on', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_on', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('updated_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('users')
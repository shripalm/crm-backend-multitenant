"""add contact gender address to users

Revision ID: a1b2c3d4e5a9
Revises: a1b2c3d4e5a8
Create Date: 2025-12-16 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5a9'
down_revision = 'a1b2c3d4e5a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('contact', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(10), nullable=True))
    op.add_column('users', sa.Column('address', sa.Text, nullable=True))


def downgrade() -> None:
    # Remove the columns
    op.drop_column('users', 'address')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'contact')

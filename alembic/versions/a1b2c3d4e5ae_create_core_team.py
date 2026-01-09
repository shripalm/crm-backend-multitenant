"""create core_team table

Revision ID: a1b2c3d4e5ae
Revises: a1b2c3d4e5ad
Create Date: 2026-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5ae'
down_revision = 'a1b2c3d4e5ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('core_team',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('number', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('core_team')

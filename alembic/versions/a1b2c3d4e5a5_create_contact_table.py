"""create contacts table

Revision ID: a1b2c3d4e5a5
Revises: a1b2c3d4e5a2
Create Date: 2025-12-03 10:55:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5a5'
down_revision = 'a1b2c3d4e5a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create contacts table
    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("contact_no", sa.String(20), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("project_name", sa.String(255), nullable=True),
        sa.Column("property_type", sa.String(100), nullable=True),
        sa.Column("budget_range", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create indexes for better query performance
    op.create_index("ix_contacts_name", "contacts", ["name"])
    op.create_index("ix_contacts_email", "contacts", ["email"])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("ix_contacts_email", table_name="contacts")
    op.drop_index("ix_contacts_name", table_name="contacts")
    
    # Drop table
    op.drop_table("contacts")

"""create call_reports table

Revision ID: a1b2c3d4e5a6
Revises: a1b2c3d4e5a5
Create Date: 2025-12-05 10:40:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5a6'
down_revision = 'a1b2c3d4e5a5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create call_reports table with contact_id foreign key
    op.create_table(
        "call_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tags", sa.String(255), nullable=True),
        sa.Column("sales_agent", sa.String(255), nullable=True),
        sa.Column("assigned_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_remark", sa.Text(), nullable=True),
        sa.Column("status", sa.String(100), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("employee_id", sa.String(50), nullable=True),
        sa.Column("call_duration", sa.Integer(), nullable=True),
        sa.Column("next_follow_up", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create indexes for better query performance
    op.create_index("ix_call_reports_contact_id", "call_reports", ["contact_id"])
    op.create_index("ix_call_reports_employee_id", "call_reports", ["employee_id"])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("ix_call_reports_employee_id", table_name="call_reports")
    op.drop_index("ix_call_reports_contact_id", table_name="call_reports")
    
    # Drop table
    op.drop_table("call_reports")

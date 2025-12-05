"""create leads, site_visits and tasks tables

Revision ID: a1b2c3d4e5a7
Revises: a1b2c3d4e5a6
Create Date: 2025-12-05 13:15:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5a7"
down_revision = "a1b2c3d4e5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create leads table
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contacts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("sales_task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("site_visit", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("call_duration", sa.Integer(), nullable=True),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    op.create_index("ix_leads_contact_id", "leads", ["contact_id"])
    op.create_index("ix_leads_employee_id", "leads", ["employee_id"])

    # Create site_visits table
    op.create_table(
        "site_visits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "assigned_to_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contacts.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("visit_frequency", sa.String(50), nullable=True),
        sa.Column("schedule_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("last_visited_date", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_site_visits_contact_id", "site_visits", ["contact_id"])
    op.create_index("ix_site_visits_assigned_to_id", "site_visits", ["assigned_to_id"])

    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("status", sa.String(100), nullable=True),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("assigned_to_team", sa.String(255), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("callback_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("ix_tasks_lead_id", "tasks", ["lead_id"])



def downgrade() -> None:
    # Drop indexes and tables in reverse order
    op.drop_index("ix_tasks_lead_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_site_visits_assigned_to_id", table_name="site_visits")
    op.drop_index("ix_site_visits_contact_id", table_name="site_visits")
    op.drop_table("site_visits")

    op.drop_index("ix_leads_employee_id", table_name="leads")
    op.drop_index("ix_leads_contact_id", table_name="leads")
    op.drop_table("leads")

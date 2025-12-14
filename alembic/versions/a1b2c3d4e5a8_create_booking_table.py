"""create booking table

Revision ID: a1b2c3d4e5a8
Revises: a1b2c3d4e5a7           
Create Date: 2025-12-05 13:30:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5a8"
down_revision = "a1b2c3d4e5a7"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create bookings table
    op.create_table(
        "bookings",
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "site_visit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("site_visits.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("booking_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_status", sa.String(length=50), nullable=True),
        sa.Column("payment_paid", sa.String(length=50), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_mode", sa.String(length=50), nullable=True),
        sa.Column("last_follow_up", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stage", sa.String(length=50), nullable=True),
    )

    op.create_index("ix_bookings_site_visit_id", "bookings", ["site_visit_id"])


def downgrade() -> None:
    # Drop bookings table
    op.drop_index("ix_bookings_site_visit_id", table_name="bookings")
    op.drop_table("bookings")
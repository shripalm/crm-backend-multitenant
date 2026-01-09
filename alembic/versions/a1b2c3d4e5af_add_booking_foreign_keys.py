"""add core_team/project/property foreign keys to bookings

Revision ID: a1b2c3d4e5af
Revises: a1b2c3d4e5ae
Create Date: 2026-01-09 09:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5af"
down_revision = "a1b2c3d4e5ae"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    """Return True if the given column already exists on the table.

    This makes the migration idempotent across tenant databases where
    some columns might already be present (e.g. manually added).
    """

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in existing


def upgrade() -> None:
    """Add core_team_id, project_id, property_id columns and FKs to bookings.

    This migration is designed to align the PostgreSQL schema with the
    existing SQLAlchemy Booking model without touching existing data.
    All new columns are nullable and use SET NULL on delete.
    """

    # Add columns (nullable so existing rows remain valid). Guard with
    # existence checks so we don't fail with DuplicateColumnError in
    # tenants where these columns were already created.
    if not _column_exists("bookings", "core_team_id"):
        op.add_column(
            "bookings",
            sa.Column(
                "core_team_id",
                postgresql.UUID(as_uuid=True),
                nullable=True,
            ),
        )

    if not _column_exists("bookings", "project_id"):
        op.add_column(
            "bookings",
            sa.Column(
                "project_id",
                postgresql.UUID(as_uuid=True),
                nullable=True,
            ),
        )

    if not _column_exists("bookings", "property_id"):
        op.add_column(
            "bookings",
            sa.Column(
                "property_id",
                postgresql.UUID(as_uuid=True),
                nullable=True,
            ),
        )

    # Create foreign key constraints
    op.create_foreign_key(
        "fk_bookings_core_team_id_core_team",
        source_table="bookings",
        referent_table="core_team",
        local_cols=["core_team_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_bookings_project_id_projects",
        source_table="bookings",
        referent_table="projects",
        local_cols=["project_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_bookings_property_id_properties",
        source_table="bookings",
        referent_table="properties",
        local_cols=["property_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Drop booking FKs and columns.

    Note: This only removes the three new columns/constraints and does not
    affect existing booking data in other columns.
    """

    # Drop foreign keys first
    op.drop_constraint(
        "fk_bookings_property_id_properties",
        "bookings",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_bookings_project_id_projects",
        "bookings",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_bookings_core_team_id_core_team",
        "bookings",
        type_="foreignkey",
    )

    # Then drop columns
    op.drop_column("bookings", "property_id")
    op.drop_column("bookings", "project_id")
    op.drop_column("bookings", "core_team_id")

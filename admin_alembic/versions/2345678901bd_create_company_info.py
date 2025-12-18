"""
Docstring for admin_alembic.versions.2345678902cd_create_company_info

Revision ID: 2345678901bd
Revises: 2345678901bc
Create Date: 2025-12-16 11:20:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = "2345678901bd"
down_revision = "2345678901bc"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create company_info table
    op.create_table(
        "company_info",
        sa.Column("company_id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column(
            "company_size",
            sa.Enum(
                "EMP_1_10",
                "EMP_11_50",
                "EMP_51_200",
                "EMP_201_500",
                "EMP_500_PLUS",
                name="company_size",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text, nullable=True),
    )

    op.create_index("ix_company_info_name", "company_info", ["name"], unique=False)

def downgrade() -> None:
    # Drop company_info table
    op.drop_index("ix_company_info_name", table_name="company_info")
    op.drop_table("company_info")
    
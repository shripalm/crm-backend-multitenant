import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base

# Association table: user ↔ role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("user_id", "role_id", name="uq_user_role"),
)

# Association table: role ↔ permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
)

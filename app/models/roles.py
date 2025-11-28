import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.mappings import user_roles, role_permissions


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )

    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
    )

    def __repr__(self):
        return f"<Role name={self.name}>"

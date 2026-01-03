import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.mappings import user_roles


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    team_name = Column(String(255), nullable=True)
    agent_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # New fields
    contact = Column(String(20), nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="joined",
    )

    def __repr__(self):
        return f"<User email={self.email}>"

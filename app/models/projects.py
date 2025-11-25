from sqlalchemy import Column, Text, Date, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import sqlalchemy as sa

from app.db.base_class import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"))
    name = Column(Text, nullable=False)
    developer = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    meta = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))

    # relationship to properties
    properties = relationship("Property", back_populates="project", cascade="all, delete-orphan")


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    unit_number = Column(Text, nullable=True)
    size = Column(Numeric, nullable=True)
    price = Column(Numeric, nullable=True)
    status = Column(Text, nullable=True)
    attributes = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))

    project = relationship("Project", back_populates="properties")

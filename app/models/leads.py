import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    sales_task_id = Column(UUID(as_uuid=True), nullable=True)
    remark = Column(Text, nullable=True)
    site_visit = Column(Boolean, default=False)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    call_duration = Column(Integer, nullable=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Lead id={self.id} contact_id={self.contact_id}>"

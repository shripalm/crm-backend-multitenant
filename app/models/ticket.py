import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func

from app.db.base_class import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ticket classification
    category = Column(String(100), nullable=False)  # e.g. "SYSTEM", "GENERAL"

    # Associations
    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
    )
    raised_by = Column(UUID(as_uuid=True), nullable=False)  # ID of user/agent who raised

    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(50), nullable=False)  # e.g. "LOW", "MEDIUM", "HIGH"
    status = Column(String(50), nullable=False)  # e.g. "OPEN","CLOSED","RESOLVED"

    # Attachments (list of URLs)
    attachment_urls = Column(ARRAY(String), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Ticket id={self.id} category={self.category} status={self.status}>"

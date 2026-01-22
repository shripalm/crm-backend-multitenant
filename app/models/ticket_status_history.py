import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class TicketStatusHistory(Base):
    __tablename__ = "ticket_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)

    changed_by_id = Column(UUID(as_uuid=True), nullable=True)
    changed_by_type = Column(String(20), nullable=True)  # 'user' | 'agent' | 'admin'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TicketStatusHistory ticket_id={self.ticket_id} {self.old_status}->{self.new_status}>"

import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_role = Column(
        String(50),
        nullable=False,
    )  # SUPER_ADMIN | AGENT | USER

    comment = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TicketComment id={self.id} ticket_id={self.ticket_id}>"

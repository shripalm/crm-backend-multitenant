import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class SiteVisit(Base):
    __tablename__ = "site_visits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=True,
    )

    visit_frequency = Column(String(50), nullable=True)
    schedule_date = Column(DateTime(timezone=True), nullable=True)
    remark = Column(Text, nullable=True)
    lead_id = Column(UUID(as_uuid=True), nullable=True)
    last_visited_date = Column(DateTime(timezone=True), nullable=True)

    assigned_to = relationship("User", backref="site_visits")
    contact = relationship("Contact", backref="site_visits")

    def __repr__(self):
        return f"<SiteVisit id={self.id} contact_id={self.contact_id}>"


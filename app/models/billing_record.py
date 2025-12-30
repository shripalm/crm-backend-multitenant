import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class BillingRecord(Base):
    __tablename__ = "billing_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    billing_month = Column(Date(), nullable=False, index=True)
    active_users = Column(Integer(), nullable=False)
    price_per_user = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)

    status = Column(String(20), nullable=False, server_default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<BillingRecord agent_id={self.agent_id} billing_month={self.billing_month} total_amount={self.total_amount} status={self.status}>"

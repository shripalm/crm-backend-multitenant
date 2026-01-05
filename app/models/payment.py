import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.enums.payment_enums import PaymentStatus

class Payment(Base):
    """Payment model representing individual payment transactions."""
    
    __tablename__ = "crm_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Agent who is trying to pay
    user_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # External gateway identifiers
    order_id = Column(String(100), unique=True, nullable=False, index=True)  # Paytm orderId
    txn_id = Column(String(100), nullable=True, index=True)  # Paytm txnId (populated after success)
    
    # Financial details
    amount = Column(Numeric(10, 2), nullable=False)
    
    # CONTEXT LOCK: Store plan_code, purpose, and duration here to enforce it later
    # e.g. {"plan_code": "PRO", "duration_days": 30, "purpose": "SUBSCRIPTION"}
    payment_context = Column(JSONB, nullable=False)
    
    status = Column(
        Enum(PaymentStatus, name="payment_status"),
        nullable=False,
        default=PaymentStatus.INITIATED,
        index=True
    )
    
    raw_response = Column(JSONB, nullable=True) # Gateway callback data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Payment order_id={self.order_id} amount={self.amount} status={self.status.value}>"

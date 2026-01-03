"""
Refund model for CRM payment system.

Represents refund transactions against successful payments.
Maintains both internal tracking and external gateway references.
"""

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.enums.payment_enums import RefundStatus


class Refund(Base):
    """Refund model representing refund transactions against payments."""
    
    __tablename__ = "crm_refunds"

    # Primary key - internal UUID, independent of external systems
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to payment
    payment_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("crm_payments.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # External gateway identifiers
    ref_id = Column(String(100), unique=True, nullable=False, index=True)  # Merchant-side refund reference
    refund_id = Column(String(100), nullable=True, index=True)  # Paytm refundId (populated after success)
    
    # Financial details
    refund_amount = Column(Numeric(10, 2), nullable=False)
    
    # Refund status
    status = Column(
        Enum(RefundStatus, name="refund_status"),
        nullable=False,
        default=RefundStatus.INITIATED,
        index=True
    )
    
    # Raw gateway response for audit/debugging
    raw_response = Column(JSONB, nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<Refund ref_id={self.ref_id} amount={self.refund_amount} status={self.status.value}>"

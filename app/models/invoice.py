import uuid
from sqlalchemy import Column, String, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.enums.payment_enums import InvoiceStatus

class Invoice(Base):
    """Invoice model representing proof of payment."""
    
    __tablename__ = "crm_invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Human-readable invoice number (e.g., INV-2025-000123)
    invoice_no = Column(String(50), unique=True, nullable=False, index=True)
    
    # REQUIRED: Reference to the successful payment
    payment_id = Column(UUID(as_uuid=True), ForeignKey("crm_payments.id"), nullable=False, unique=True)
    
    # Reference to agent
    user_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    
    # Snapshot of data from payment
    amount = Column(Numeric(10, 2), nullable=False)
    plan_code = Column(String(50), nullable=True)
    purpose = Column(String(50), nullable=False, default="SUBSCRIPTION")
    
    status = Column(
        Enum(InvoiceStatus, name="invoice_status"),
        nullable=False,
        default=InvoiceStatus.PAID, # In our new model, invoices are only created if PAID
        index=True
    )
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Invoice invoice_no={self.invoice_no} amount={self.amount}>"

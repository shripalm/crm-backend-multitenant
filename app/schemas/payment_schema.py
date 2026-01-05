from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.enums.payment_enums import InvoiceStatus, PaymentStatus, RefundStatus

# ==============================
# SUBSCRIPTION PAYMENT SCHEMAS
# ==============================

class InitiateAgentPaymentRequest(BaseModel):
    """Request to initiate a subscription payment."""
    target_agent_id: UUID = Field(..., description="UUID of the agent receiving the subscription")
    plan_code: str = Field(..., description="e.g. BASIC, PRO, ENTERPRISE")
    amount: Decimal = Field(..., gt=0, description="Fixed amount for the plan")
    amount: Decimal = Field(..., gt=0, description="Fixed amount for the plan")
    duration_days: int = Field(default=30, description="Validity period")

class InitiateSelfPaymentRequest(BaseModel):
    """Request for agent to initiate their own subscription payment."""
    plan_code: str = Field(..., description="Plan code (BASIC, PRO, ENTERPRISE)")
    duration_days: int = Field(default=30, description="Validity period")


class PaymentInitiationResponse(BaseModel):
    """Response after initiating payment."""
    order_id: str
    status: PaymentStatus
    amount: float = Field(..., description="Payment amount", example=2499.00)
    currency: str = "INR"

class SubscriptionStatusResponse(BaseModel):
    """Current subscription status for the agent."""
    is_active: bool
    plan_code: Optional[str] = None
    expiry_date: Optional[datetime] = None
    message: str

# ==============================
# INVOICE SCHEMAS (Post-Payment)
# ==============================

class InvoiceRead(BaseModel):
    """Response schema for a generated invoice receipt."""
    id: UUID
    invoice_no: str
    amount: Decimal
    plan_code: str
    status: InvoiceStatus
    created_at: datetime

    class Config:
        from_attributes = True

# ==============================
# CALLBACK LAYOUT
# ==============================

class PaytmCallbackSchema(BaseModel):
    """Paytm specific callback schema."""
    ORDERID: str
    TXNID: str
    STATUS: str
    TXNAMOUNT: str
    # ... other paytm fields

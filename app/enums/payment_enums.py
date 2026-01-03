"""
Payment system enums for CRM application.

Defines status enums for invoices, payments, and refunds.
These enums provide type safety and consistent status tracking
across the payment system.
"""

from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice lifecycle statuses."""
    CREATED = "CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentStatus(str, Enum):
    """Payment transaction statuses."""
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class RefundStatus(str, Enum):
    """Refund transaction statuses."""
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class PaymentPlan(str, Enum):
    """Available subscription plans."""
    BASIC = "BASIC"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"

# Pricing Configuration (In a real app, this would be in DB)
from decimal import Decimal
PRICING_PLANS = {
    PaymentPlan.BASIC: Decimal("999.00"),
    PaymentPlan.PRO: Decimal("2499.00"),
    PaymentPlan.ENTERPRISE: Decimal("4999.00")
}

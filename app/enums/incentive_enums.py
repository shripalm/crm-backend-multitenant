from enum import Enum


class IncentiveType(str, Enum):
    """Enum for types of incentive calculations"""
    FIXED = "fixed"  # Call-based fixed amount (e.g., ₹500 per 1000 calls)
    PERCENTAGE = "percentage"  # Percentage of deal value


class IncentiveCalculationStatus(str, Enum):
    """Enum for tracking incentive calculation status"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"

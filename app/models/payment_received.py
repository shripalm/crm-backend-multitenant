import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class PaymentReceived(Base):
    __tablename__ = "payment_received"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to Booking
    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.booking_id"),
        nullable=True,
    )

    # URL to the stored receipt
    receipt = Column(String(512), nullable=True)

    # Stage of the payment / process
    stage = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    booking = relationship("Booking", backref="payments_received")

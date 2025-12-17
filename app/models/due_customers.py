import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class DueCustomer(Base):
    __tablename__ = "due_customers"

    # Use booking_id as the primary key, assuming one due-customer record per booking
    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.booking_id"),
        primary_key=True,
    )

    last_follow_up_date = Column(DateTime(timezone=True), nullable=True)
    next_follow_up_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=True)

    # Relationship back to Booking
    booking = relationship("Booking", backref="due_customer", uselist=False)

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID     
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    site_visit_id = Column(UUID(as_uuid=True), 
                           ForeignKey("site_visits.id"), on_delete="SET NULL",
                           nullable=True)

    booking_date = Column(DateTime(timezone=True), nullable=True)
    payment_status = Column(String(50), nullable=True)
    payment_paid = Column(String(50), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    payment_mode = Column(String(50), nullable=True)
    last_follow_up = Column(DateTime(timezone=True), nullable=True)
    stage = Column(String(50), nullable=True)
    

    site_visit = relationship("SiteVisit", backref="bookings")

    def __repr__(self):
        return f"<Booking id={self.booking_id} booking_date={self.booking_date}>"
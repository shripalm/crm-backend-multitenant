import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class CallReport(Base):
    __tablename__ = "call_reports"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Contact Reference (Foreign Key)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # CRM Fields
    tags = Column(String(255), nullable=True)  # e.g., "Hot Lead", "Follow-up Required"
    sales_agent = Column(String(255), nullable=True)  # Sales person name
    assigned_date = Column(DateTime(timezone=True), nullable=True)  # When lead was assigned
    last_activity_date = Column(DateTime(timezone=True), nullable=True)  # Last interaction date
    remark = Column(Text, nullable=True)  # Detailed notes about last activity
    status = Column(String(100), nullable=True)  # e.g., "New", "In Progress", "Closed", "Won", "Lost"
    source = Column(String(100), nullable=True)  # e.g., "Website", "Referral", "Cold Call"
    
    # Employee & Call Details
    employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # Employee identifier
    call_duration = Column(Integer, nullable=True)  # Duration in seconds
    next_follow_up = Column(DateTime(timezone=True), nullable=True)  # Next scheduled follow-up
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship to Contact
    contact = relationship("Contact", back_populates="call_reports")

    def __repr__(self):
        return f"<CallReport id={self.id} contact_id={self.contact_id} status={self.status}>"

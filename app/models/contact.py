import uuid
from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Contact(Base):
    __tablename__ = "contacts"

    # Sr.No will be auto-generated as id
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    contact_no = Column(String(20), nullable=True)
    
    # Location Information
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    
    # Lead Information
    source = Column(String(100), nullable=True)  # e.g., "Website", "Referral", "Advertisement"
    project_name = Column(String(255), nullable=True)
    property_type = Column(String(100), nullable=True)  # e.g., "Apartment", "Villa", "Plot"
    budget_range = Column(String(100), nullable=True)  # e.g., "50L-1Cr", "1Cr-2Cr"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    call_reports = relationship("CallReport", back_populates="contact", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Contact name={self.name} email={self.email}>"

import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class Task(Base):
    __tablename__ = "tasks"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Lead Reference
    lead_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Reference to lead/contact
    
    # Task Details
    status = Column(String(100), nullable=True)  # e.g., "Pending", "In Progress", "Completed", "Cancelled"
    assigned_to = Column(UUID(as_uuid=True), nullable=True)  # User/Employee name assigned to this task
    assigned_to_team = Column(String(255), nullable=True)  # Team name assigned to this task
    assigned_by = Column(UUID(as_uuid=True), nullable=True)  # User/Employee name who assigned this task
    remarks = Column(Text, nullable=True)  # Detailed notes/comments about the task
    callback_time = Column(DateTime(timezone=True), nullable=True)  # Scheduled callback date/time
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Task id={self.id} status={self.status} assigned_to={self.assigned_to}>"

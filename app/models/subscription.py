import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base

class UserSubscription(Base):
    """Tracks active access for agents."""
    
    __tablename__ = "crm_user_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    plan_code = Column(String(50), nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserSubscription user_id={self.user_id} plan={self.plan_code} active={self.is_active}>"

"""Agent OTP Model for password reset verification."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class AgentOTP(Base):
    """OTP storage for agent password reset verification."""
    
    __tablename__ = "agent_otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email = Column(String(255), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    reset_token = Column(String(255), nullable=True, unique=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<AgentOTP email={self.email} verified={self.is_verified}>"

    def is_expired(self) -> bool:
        """Check if OTP has expired."""
        return datetime.now(self.expires_at.tzinfo) > self.expires_at

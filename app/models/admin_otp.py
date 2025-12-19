"""Admin OTP Model for password reset verification."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class AdminOTP(Base):
    """OTP storage for admin password reset verification."""
    
    __tablename__ = "admin_otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(
        Integer,
        ForeignKey("admin.id", ondelete="CASCADE"),
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
        return f"<AdminOTP email={self.email} verified={self.is_verified}>"

    def is_expired(self) -> bool:
        """Check if OTP has expired."""
        return datetime.now(self.expires_at.tzinfo) > self.expires_at

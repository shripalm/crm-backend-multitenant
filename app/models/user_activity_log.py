import uuid

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    login_time = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<UserActivityLog agent_id={self.agent_id} user_id={self.user_id} login_time={self.login_time}>"

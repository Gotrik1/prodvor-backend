# app/models/user_session.py
import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base

class UserSession(Base):
    __tablename__ = "user_session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    refresh_token = Column(String, nullable=False)
    user_agent = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

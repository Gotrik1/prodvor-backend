from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User

class NotificationType(enum.Enum):
    FRIEND_REQUEST = "friend_request"
    FRIEND_ACCEPT = "friend_accept"
    TEAM_INVITE = "team_invite"
    TEAM_ACCEPT = "team_accept"
    LFG_POST = "lfg_post"

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    message: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship('User', back_populates='notifications')

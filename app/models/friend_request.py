from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User

class FriendRequest(Base):
    __tablename__ = 'friend_requests'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    to_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(String, default='pending') # pending, accepted, declined
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id], back_populates="friend_requests_sent")
    to_user: Mapped["User"] = relationship("User", foreign_keys=[to_user_id], back_populates="friend_requests_received")

from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
import enum
from sqlalchemy import Column, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User

class FriendRequestStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"

class FriendRequest(Base):
    __tablename__ = 'friend_requests'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    receiver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    status: Mapped[FriendRequestStatus] = mapped_column(Enum(FriendRequestStatus), default=FriendRequestStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id], back_populates="sent_friend_requests")
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id], back_populates="received_friend_requests")

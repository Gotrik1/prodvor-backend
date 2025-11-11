from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User
    from .event import Event

class UserEvent(Base):
    __tablename__ = 'user_event'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('event.id'))

    user: Mapped["User"] = relationship("User", back_populates="user_events")
    event: Mapped["Event"] = relationship("Event", back_populates="users")

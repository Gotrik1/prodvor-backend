from __future__ import annotations
from typing import List, TYPE_CHECKING
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .team_event import TeamEvent
    from .sport_event import SportEvent
    from .user_event import UserEvent

class Event(Base):
    __tablename__ = "event"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=True)
    organizer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organizer: Mapped["User"] = relationship(back_populates="events")
    teams: Mapped[List["TeamEvent"]] = relationship("TeamEvent", back_populates="event")
    sports: Mapped[List["SportEvent"]] = relationship("SportEvent", back_populates="event")
    users: Mapped[List["UserEvent"]] = relationship("UserEvent", back_populates="event")

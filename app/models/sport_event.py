from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base

if TYPE_CHECKING:
    from .sport import Sport
    from .event import Event

class SportEvent(Base):
    __tablename__ = 'sport_event'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport_id: Mapped[int] = mapped_column(Integer, ForeignKey('sports.id'))
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('event.id'))

    sport: Mapped["Sport"] = relationship("Sport", back_populates="sport_events")
    event: Mapped["Event"] = relationship("Event", back_populates="sports")

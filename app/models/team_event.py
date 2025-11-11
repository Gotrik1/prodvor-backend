from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base

if TYPE_CHECKING:
    from .team import Team
    from .event import Event

class TeamEvent(Base):
    __tablename__ = 'team_event'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('teams.id'))
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('event.id'))

    team: Mapped["Team"] = relationship("Team", back_populates="team_events")
    event: Mapped["Event"] = relationship("Event", back_populates="teams")

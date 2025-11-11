from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base_class import Base
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .team import Team

class UserTeam(Base):
    __tablename__ = 'user_team'
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="team_associations")
    team: Mapped["Team"] = relationship(back_populates="member_associations")

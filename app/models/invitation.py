from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User
    from .team import Team

class Invitation(Base):
    __tablename__ = 'invitations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('teams.id'))
    status: Mapped[str] = mapped_column(String, default='pending')

    user: Mapped["User"] = relationship('User', back_populates='invitations')
    team: Mapped["Team"] = relationship('Team', back_populates='invitations')

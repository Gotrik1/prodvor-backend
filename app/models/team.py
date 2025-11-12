from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional
from sqlalchemy import Column, String, Integer, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
import uuid
from datetime import datetime

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User
    from .user_team import UserTeam
    from .invitation import Invitation
    from .team_event import TeamEvent
    from .post import Post
    from .lfg import LFG

team_followers = Table(
    'team_followers', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('team_id', UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True)
)

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    logoUrl: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    captain_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    game: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, default=1200)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    captain: Mapped["User"] = relationship("User")
    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary=team_followers,
        backref="followed_teams"
    )
    member_associations: Mapped[List["UserTeam"]] = relationship(back_populates="team")
    members: AssociationProxy[List["User"]] = association_proxy("member_associations", "user")
    invitations: Mapped[List["Invitation"]] = relationship('Invitation', back_populates='team', cascade="all, delete-orphan")
    team_events: Mapped[List["TeamEvent"]] = relationship("TeamEvent", back_populates="team")
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="team")
    lfgs: Mapped[List["LFG"]] = relationship("LFG", back_populates="team")

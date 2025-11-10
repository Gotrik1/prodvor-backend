from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
import uuid

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User
    from .user_team import UserTeam

team_followers = Table(
    'team_followers', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('team_id', UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True)
)

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    logoUrl: Mapped[str] = mapped_column(String(200))
    captainId: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    game: Mapped[str] = mapped_column(String(100))
    rank: Mapped[int] = mapped_column(Integer, default=1200)
    city: Mapped[str] = mapped_column(String(100))

    captain: Mapped["User"] = relationship("User")
    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary=team_followers,
        backref="followed_teams"
    )
    member_associations: Mapped[List["UserTeam"]] = relationship(back_populates="team")
    members: list["User"] = association_proxy("member_associations", "user")

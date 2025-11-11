# app/models/user.py
from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
import uuid
from datetime import datetime

from app.db.base_class import Base

if TYPE_CHECKING:
    from .team import Team
    from .user_team import UserTeam
    from .session import Session
    from .comment import Comment
    from .notification import Notification
    from .friend_request import FriendRequest
    from .coach_profile import CoachProfile
    from .player_profile import PlayerProfile
    from .referee_profile import RefereeProfile
    from .post import Post
    from .like import Like
    from .invitation import Invitation

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    firstName: Mapped[str] = mapped_column(String(100))
    lastName: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_path: Mapped[str] = mapped_column(String, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship('Comment', back_populates='author', cascade="all, delete-orphan")
    posts: Mapped[List["Post"]] = relationship('Post', back_populates='author', cascade="all, delete-orphan")
    likes: Mapped[List["Like"]] = relationship('Like', back_populates='user', cascade="all, delete-orphan")
    invitations: Mapped[List["Invitation"]] = relationship('Invitation', back_populates='user', cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship('Notification', back_populates='user', cascade="all, delete-orphan")

    friend_requests_sent: Mapped[List["FriendRequest"]] = relationship('FriendRequest', foreign_keys='FriendRequest.from_user_id', backref='from_user', cascade="all, delete-orphan")
    friend_requests_received: Mapped[List["FriendRequest"]] = relationship('FriendRequest', foreign_keys='FriendRequest.to_user_id', backref='to_user', cascade="all, delete-orphan")

    team_associations: Mapped[List["UserTeam"]] = relationship(back_populates="user")
    teams = association_proxy("team_associations", "team")
    # team_applications = relationship('TeamApplication', back_populates='user', cascade="all, delete-orphan")

    coach_profiles: Mapped["CoachProfile"] = relationship("CoachProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    player_profiles: Mapped["PlayerProfile"] = relationship("PlayerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    referee_profiles: Mapped["RefereeProfile"] = relationship("RefereeProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # user_settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # user_privacy_settings = relationship("UserPrivacySettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # looking_for_game = relationship("LookingForGame", back_populates="user", uselist=False, cascade="all, delete-orphan")

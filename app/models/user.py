# app/models/user.py
from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
import uuid
from datetime import datetime

from app.db.base_class import Base
from .user_settings import UserSettings
from .user_privacy_settings import UserPrivacySettings

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
    from .lfg import LFG
    from .user_favorite_sport import UserFavoriteSport
    from .event import Event
    from .user_event import UserEvent

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    s3_path: Mapped[str] = mapped_column(String, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship('Comment', back_populates='author', cascade="all, delete-orphan")
    posts: Mapped[List["Post"]] = relationship('Post', back_populates='author', cascade="all, delete-orphan")
    likes: Mapped[List["Like"]] = relationship('Like', back_populates='user', cascade="all, delete-orphan")
    invitations: Mapped[List["Invitation"]] = relationship('Invitation', back_populates='user', cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship('Notification', back_populates='user', cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship(back_populates="organizer")

    sent_friend_requests: Mapped[List["FriendRequest"]] = relationship('FriendRequest', foreign_keys='FriendRequest.requester_id', back_populates='requester', cascade="all, delete-orphan")
    received_friend_requests: Mapped[List["FriendRequest"]] = relationship('FriendRequest', foreign_keys='FriendRequest.receiver_id', back_populates='receiver', cascade="all, delete-orphan")

    team_associations: Mapped[List["UserTeam"]] = relationship(back_populates="user")
    teams = association_proxy("team_associations", "team")
    
    coach_profiles: Mapped[List["CoachProfile"]] = relationship("CoachProfile", back_populates="user", cascade="all, delete-orphan")
    player_profiles: Mapped[List["PlayerProfile"]] = relationship("PlayerProfile", back_populates="user", cascade="all, delete-orphan")
    referee_profiles: Mapped[List["RefereeProfile"]] = relationship("RefereeProfile", back_populates="user", cascade="all, delete-orphan")

    user_settings: Mapped["UserSettings"] = relationship("UserSettings", back_populates="user", cascade="all, delete-orphan")
    user_privacy_settings: Mapped["UserPrivacySettings"] = relationship("UserPrivacySettings", back_populates="user", cascade="all, delete-orphan")
    lfgs: Mapped[List["LFG"]] = relationship("LFG", back_populates="creator", cascade="all, delete-orphan")
    favorite_sports: Mapped[List["UserFavoriteSport"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    user_events: Mapped[List["UserEvent"]] = relationship("UserEvent", back_populates="user")

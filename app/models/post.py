from __future__ import annotations
from typing import TYPE_CHECKING, List
import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base
from datetime import datetime

if TYPE_CHECKING:
    from .comment import Comment
    from .like import Like
    from .user import User
    from .team import Team

class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comments: Mapped[List["Comment"]] = relationship('Comment', back_populates='post', cascade="all, delete-orphan")
    likes: Mapped[List["Like"]] = relationship('Like', back_populates='post', cascade="all, delete-orphan")
    author: Mapped["User"] = relationship("User", back_populates="posts")
    team: Mapped["Team"] = relationship("Team", back_populates="posts")

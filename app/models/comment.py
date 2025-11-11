from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base
from datetime import datetime

if TYPE_CHECKING:
    from .post import Post
    from .user import User

class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    postId: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('posts.id'), nullable=False)
    authorId: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    post: Mapped["Post"] = relationship('Post', back_populates='comments')
    author: Mapped["User"] = relationship('User', back_populates='comments')

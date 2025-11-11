from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User
    from .post import Post

class Like(Base):
    __tablename__ = 'likes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'))

    user: Mapped["User"] = relationship('User', back_populates='likes')
    post: Mapped["Post"] = relationship('Post', back_populates='likes')

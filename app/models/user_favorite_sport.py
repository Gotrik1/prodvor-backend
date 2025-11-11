from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User
    from .sport import Sport

class UserFavoriteSport(Base):
    __tablename__ = 'user_favorite_sport'
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    sport_id: Mapped[int] = mapped_column(Integer, ForeignKey('sports.id'), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="favorite_sports")
    sport: Mapped["Sport"] = relationship("Sport", back_populates="favorited_by_users")

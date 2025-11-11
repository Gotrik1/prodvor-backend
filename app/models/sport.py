from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base_class import Base
from datetime import datetime

if TYPE_CHECKING:
    from .user_favorite_sport import UserFavoriteSport
    from .sport_event import SportEvent

class Sport(Base):
    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    isTeamSport: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    favorited_by_users: Mapped[List["UserFavoriteSport"]] = relationship(back_populates="sport", cascade="all, delete-orphan")
    sport_events: Mapped[List["SportEvent"]] = relationship(back_populates="sport")

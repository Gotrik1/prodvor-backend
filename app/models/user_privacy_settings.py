from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User

class UserPrivacySettings(Base):
    __tablename__ = 'user_privacy_settings'
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True, nullable=False, unique=True)
    profile_visibility: Mapped[str] = mapped_column(String(50), default='all')
    teams_visibility: Mapped[str] = mapped_column(String(50), default='all')
    messages_privacy: Mapped[str] = mapped_column(String(50), default='friends')

    user: Mapped["User"] = relationship("User", back_populates="user_privacy_settings")

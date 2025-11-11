# app/models/referee_profile.py
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from datetime import datetime

if TYPE_CHECKING:
    from .user import User

class RefereeProfile(Base):
    __tablename__ = "referee_profile"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="referee_profiles")

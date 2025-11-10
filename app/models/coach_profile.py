# app/models/coach_profile.py
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class CoachProfile(Base):
    __tablename__ = "coach_profile"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)

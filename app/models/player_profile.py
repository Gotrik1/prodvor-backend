# app/models/player_profile.py
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class PlayerProfile(Base):
    __tablename__ = "player_profile"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)

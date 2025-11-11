import uuid
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Quest(Base):
    __tablename__ = 'quests'
    name = Column(String(150))
    description = Column(Text)
    type = Column(String(50))
    xp_reward = Column(Integer)

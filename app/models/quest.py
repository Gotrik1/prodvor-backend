import uuid
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Quest(Base):
    __tablename__ = 'quests'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150))
    description = Column(Text)
    type = Column(String(50))
    xp_reward = Column(Integer)

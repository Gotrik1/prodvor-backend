import uuid
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Tournament(Base):
    __tablename__ = 'tournaments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150))
    startDate = Column(DateTime)
    endDate = Column(DateTime)
    maxTeams = Column(Integer)
    description = Column(String(500))

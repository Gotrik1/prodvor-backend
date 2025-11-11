import uuid
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Tournament(Base):
    __tablename__ = 'tournaments'
    name = Column(String(150))
    startDate = Column(DateTime)
    endDate = Column(DateTime)
    maxTeams = Column(Integer)
    description = Column(String(500))

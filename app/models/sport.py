from sqlalchemy import Column, String, Boolean
from app.db.base_class import Base

class Sport(Base):
    __tablename__ = "sports"

    name = Column(String, nullable=False)
    isTeamSport = Column(Boolean, nullable=False)

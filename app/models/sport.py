from sqlalchemy import Column, String, Boolean
from app.db.base_class import Base

class Sport(Base):
    __tablename__ = "sports"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    isTeamSport = Column(Boolean, nullable=False)

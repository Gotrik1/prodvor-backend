from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String)
    status = Column(String)
    organizer_id = Column(Integer, ForeignKey("user.id"))

    organizer = relationship("User", back_populates="events")
    teams = relationship("TeamEvent", back_populates="event")
    sports = relationship("SportEvent", back_populates="event")
    users = relationship("UserEvent", back_populates="event")

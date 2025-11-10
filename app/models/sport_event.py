from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class SportEvent(Base):
    __tablename__ = 'sport_event'
    id = Column(Integer, primary_key=True, index=True)
    sport_id = Column(Integer, ForeignKey('sport.id'))
    event_id = Column(Integer, ForeignKey('event.id'))

    sport = relationship("Sport", back_populates="sport_events")
    event = relationship("Event", back_populates="sports")

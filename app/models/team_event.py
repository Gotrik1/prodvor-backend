from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class TeamEvent(Base):
    __tablename__ = 'team_event'
    team_id = Column(Integer, ForeignKey('team.id'))
    event_id = Column(Integer, ForeignKey('event.id'))

    team = relationship("Team", back_populates="team_events")
    event = relationship("Event", back_populates="teams")

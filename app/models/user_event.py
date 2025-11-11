from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class UserEvent(Base):
    __tablename__ = 'user_event'
    user_id = Column(Integer, ForeignKey('user.id'))
    event_id = Column(Integer, ForeignKey('event.id'))

    user = relationship("User", back_populates="user_events")
    event = relationship("Event", back_populates="users")

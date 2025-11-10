from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class UserEvent(Base):
    __tablename__ = 'user_event'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    event_id = Column(Integer, ForeignKey('event.id'))

    user = relationship("User", back_populates="user_events")
    event = relationship("Event", back_populates="users")

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class UserFavoriteSport(Base):
    __tablename__ = 'user_favorite_sport'
    user_id = Column(Integer, ForeignKey('user.id'))
    sport_id = Column(Integer, ForeignKey('sport.id'))

    user = relationship("User", back_populates="favorite_sports")
    sport = relationship("Sport", back_populates="favorited_by_users")

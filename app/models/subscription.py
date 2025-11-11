from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True)

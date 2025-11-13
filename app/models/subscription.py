from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True)

    __table_args__ = (UniqueConstraint('user_id', 'team_id', name='_user_team_uc'),)

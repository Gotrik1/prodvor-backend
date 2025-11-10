from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base

class TeamApplication(Base):
    __tablename__ = 'team_applications'
    userId = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    teamId = Column(UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True)
    status = Column(String(20), default='pending')
    createdAt = Column(DateTime(timezone=True), server_default=func.now())

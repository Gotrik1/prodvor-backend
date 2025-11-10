import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Post(Base):
    __tablename__ = 'posts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authorId = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    teamId = Column(UUID(as_uuid=True), ForeignKey('teams.id'))
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    comments = relationship('Comment', back_populates='post', cascade="all, delete-orphan")

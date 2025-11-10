import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    postId = Column(UUID(as_uuid=True), ForeignKey('posts.id'), nullable=False)
    authorId = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship('Post', back_populates='comments')
    author = relationship('User', back_populates='comments')

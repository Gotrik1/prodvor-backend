import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(120), unique=True, nullable=False)
    nickname = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    # ... other fields from the old model can be added here
    sessions = relationship('UserSession', back_populates='user')

class UserSession(Base):
    __tablename__ = 'user_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userId = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    refreshToken = Column(String(512), nullable=False, index=True)
    userAgent = Column(String(255))
    ipAddress = Column(String(45))
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    lastActiveAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='sessions')

from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.base_class import Base

class FriendRequest(Base):
    __tablename__ = 'friend_requests'

    from_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    to_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    status = Column(String, default='pending') # pending, accepted, declined
    created_at = Column(DateTime, default=datetime.utcnow)

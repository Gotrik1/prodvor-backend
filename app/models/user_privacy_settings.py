import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class UserPrivacySettings(Base):
    __tablename__ = 'user_privacy_settings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)
    profile_visibility = Column(String(50), default='all')
    teams_visibility = Column(String(50), default='all')
    messages_privacy = Column(String(50), default='friends')

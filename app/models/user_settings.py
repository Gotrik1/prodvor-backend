import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class UserSettings(Base):
    __tablename__ = 'user_settings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)
    theme = Column(String(50), default='light')
    language = Column(String(10), default='en')

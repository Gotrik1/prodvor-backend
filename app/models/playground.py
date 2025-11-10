import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Playground(Base):
    __tablename__ = 'playgrounds'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150))
    address = Column(String(250))
    type = Column(String(100))
    surface = Column(String(100))

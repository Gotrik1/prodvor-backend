import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Sponsor(Base):
    __tablename__ = 'sponsors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150))
    logoUrl = Column(String(200))
    contribution = Column(String(200))

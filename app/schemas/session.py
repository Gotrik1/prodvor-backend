# app/schemas/session.py
from pydantic import BaseModel
import uuid
from datetime import datetime

# Base model for session data
class SessionBase(BaseModel):
    user_id: uuid.UUID
    refresh_token: str
    user_agent: str
    ip_address: str
    expires_at: datetime

# Schema for creating a new session in the database
class SessionCreate(SessionBase):
    pass

# Schema for updating an existing session
class SessionUpdate(BaseModel):
    refresh_token: str | None = None
    expires_at: datetime | None = None

# Schema for reading session data from the database
class Session(SessionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

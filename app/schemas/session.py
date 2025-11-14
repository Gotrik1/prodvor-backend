from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel


class SessionBase(BaseModel):
    user_id: uuid.UUID
    refresh_token: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    pass


class SessionInDBBase(SessionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Session(SessionInDBBase):
    pass

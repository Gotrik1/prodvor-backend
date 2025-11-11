
from pydantic import BaseModel
import uuid

class UserEventBase(BaseModel):
    user_id: uuid.UUID
    event_id: int

class UserEventCreate(UserEventBase):
    pass

class UserEventUpdate(UserEventBase):
    pass

class UserEventInDBBase(UserEventBase):
    class Config:
        from_attributes = True

class UserEvent(UserEventInDBBase):
    pass

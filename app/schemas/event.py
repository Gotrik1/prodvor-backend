from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# Shared properties
class EventBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    status: Optional[str] = None

# Properties to receive on item creation
class EventCreate(EventBase):
    name: str
    organizer_id: uuid.UUID

# Properties to receive on item update
class EventUpdate(EventBase):
    pass

# Properties shared by models in DB
class EventInDBBase(EventBase):
    id: int
    name: str
    organizer_id: uuid.UUID

    class Config:
        orm_mode = True

# Properties to return to client
class Event(EventInDBBase):
    pass

# Properties stored in DB
class EventInDB(EventInDBBase):
    pass

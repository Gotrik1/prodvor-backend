
from pydantic import BaseModel

class SportEventBase(BaseModel):
    sport_id: int
    event_id: int

class SportEventCreate(SportEventBase):
    pass

class SportEventUpdate(SportEventBase):
    pass

class SportEventInDBBase(SportEventBase):
    class Config:
        from_attributes = True

class SportEvent(SportEventInDBBase):
    pass

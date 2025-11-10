
from pydantic import BaseModel
import uuid

class TeamEventBase(BaseModel):
    team_id: uuid.UUID
    event_id: int

class TeamEventCreate(TeamEventBase):
    pass

class TeamEventUpdate(TeamEventBase):
    pass

class TeamEventInDBBase(TeamEventBase):
    class Config:
        orm_mode = True

class TeamEvent(TeamEventInDBBase):
    pass

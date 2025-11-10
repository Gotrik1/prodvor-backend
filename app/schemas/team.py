from pydantic import BaseModel
from typing import Optional, List
import uuid

# Shared properties
class TeamBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Properties to receive on item creation
class TeamCreate(TeamBase):
    name: str
    sport_id: str

# Properties to receive on item update
class TeamUpdate(TeamBase):
    pass

# Properties shared by models in DB
class TeamInDBBase(TeamBase):
    id: uuid.UUID
    name: str
    captain_id: uuid.UUID

    class Config:
        orm_mode = True

# Properties to return to client
class Team(TeamInDBBase):
    pass

# Properties stored in DB
class TeamInDB(TeamInDBBase):
    pass

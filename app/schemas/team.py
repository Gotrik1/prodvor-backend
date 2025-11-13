from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from .user import User
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    game: Optional[str] = None
    city: Optional[str] = None
    logoUrl: Optional[str] = Field(None, alias="logoUrl")

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    name: Optional[str] = None

class Team(TeamBase):
    id: UUID
    captain_id: UUID
    rank: int
    created_at: datetime
    updated_at: datetime
    members: List[User] = []

    model_config = ConfigDict(from_attributes=True)

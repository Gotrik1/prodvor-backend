from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class LFGBase(BaseModel):
    sport: str
    description: str
    required_players: int

class LFGCreate(LFGBase):
    creator_id: uuid.UUID

class LFGUpdate(LFGBase):
    pass

class LFGInDBBase(LFGBase):
    id: int
    creator_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class LFG(LFGInDBBase):
    pass

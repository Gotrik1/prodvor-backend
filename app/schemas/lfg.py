from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid
from datetime import datetime

class LFGBase(BaseModel):
    sport: str
    description: str
    required_players: int
    type: Optional[str] = None
    team_id: Optional[uuid.UUID] = None

class LFGCreate(LFGBase):
    creator_id: uuid.UUID

class LFGUpdate(LFGBase):
    pass

class LFGInDBBase(LFGBase):
    id: int
    creator_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class LFG(LFGInDBBase):
    pass

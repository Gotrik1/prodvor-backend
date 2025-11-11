
from pydantic import BaseModel
import uuid

class UserTeamBase(BaseModel):
    user_id: uuid.UUID
    team_id: uuid.UUID

class UserTeamCreate(UserTeamBase):
    pass

class UserTeamUpdate(UserTeamBase):
    pass

class UserTeamInDBBase(UserTeamBase):
    class Config:
        from_attributes = True

class UserTeam(UserTeamInDBBase):
    pass

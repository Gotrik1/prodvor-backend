from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class InvitationBase(BaseModel):
    user_id: uuid.UUID
    team_id: uuid.UUID
    status: str

class InvitationCreate(InvitationBase):
    pass

class InvitationUpdate(InvitationBase):
    pass

class InvitationInDBBase(InvitationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Invitation(InvitationInDBBase):
    pass

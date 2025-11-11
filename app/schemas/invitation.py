from pydantic import BaseModel, ConfigDict
import uuid

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
    model_config = ConfigDict(from_attributes=True)

class Invitation(InvitationInDBBase):
    pass

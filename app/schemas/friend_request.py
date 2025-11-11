from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class FriendRequestBase(BaseModel):
    requester_id: uuid.UUID
    receiver_id: uuid.UUID
    status: str

class FriendRequestCreate(FriendRequestBase):
    pass

class FriendRequestUpdate(FriendRequestBase):
    pass

class FriendRequestInDBBase(FriendRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FriendRequest(FriendRequestInDBBase):
    pass

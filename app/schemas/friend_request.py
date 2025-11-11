from pydantic import BaseModel
import uuid

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

    class Config:
        from_attributes = True

class FriendRequest(FriendRequestInDBBase):
    pass

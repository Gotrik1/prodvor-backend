from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

# Schema for creating a friend request. Client only needs to provide the receiver's ID.
class FriendRequestCreate(BaseModel):
    receiver_id: uuid.UUID

# Schema for updating a friend request. This is mostly for internal use, 
# as status updates are handled by specific endpoints (accept/decline).
class FriendRequestUpdate(BaseModel):
    status: str

# Base schema for a friend request object retrieved from the database.
class FriendRequestInDBBase(BaseModel):
    id: uuid.UUID
    requester_id: uuid.UUID
    receiver_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Public-facing schema for a friend request, to be returned by the API.
class FriendRequest(FriendRequestInDBBase):
    pass

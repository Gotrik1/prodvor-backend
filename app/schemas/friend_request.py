from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.models.friend_request import FriendRequestStatus


class FriendRequestBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FriendRequestCreate(FriendRequestBase):
    receiver_id: UUID = Field(validation_alias='to_user_id')


class FriendRequestUpdate(FriendRequestBase):
    status: Optional[FriendRequestStatus] = None


class FriendRequest(FriendRequestBase):
    id: UUID
    requester_id: UUID
    receiver_id: UUID
    status: FriendRequestStatus
    created_at: datetime

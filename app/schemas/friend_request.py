from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.friend_request import FriendRequestStatus


class FriendRequestBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FriendRequestCreate(FriendRequestBase):
    receiver_id: UUID = Field(alias="receiverId")

    @model_validator(mode="before")
    @classmethod
    def normalize_receiver_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "receiverId" in data and "receiver_id" not in data:
                data["receiver_id"] = data["receiverId"]
        return data


class FriendRequestUpdate(FriendRequestBase):
    status: Optional[FriendRequestStatus] = None


class FriendRequest(FriendRequestBase):
    id: UUID
    requester_id: UUID
    receiver_id: UUID
    status: FriendRequestStatus
    created_at: datetime

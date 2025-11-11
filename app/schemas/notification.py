from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime


class NotificationBase(BaseModel):
    user_id: uuid.UUID
    message: str


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(NotificationBase):
    pass


class NotificationInDBBase(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Notification(NotificationInDBBase):
    pass

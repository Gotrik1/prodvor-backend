from pydantic import BaseModel
import uuid


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

    class Config:
        from_attributes = True


class Notification(NotificationInDBBase):
    pass

from pydantic import BaseModel
from typing import Optional
import uuid

class SubscriptionBase(BaseModel):
    subscriber_id: uuid.UUID
    subscribed_to_id: uuid.UUID

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(SubscriptionBase):
    pass

class SubscriptionInDBBase(SubscriptionBase):
    class Config:
        orm_mode = True

class Subscription(SubscriptionInDBBase):
    pass

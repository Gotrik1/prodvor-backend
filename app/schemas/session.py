from pydantic import BaseModel
import uuid


class SessionBase(BaseModel):
    user_id: uuid.UUID


class SessionCreate(SessionBase):
    pass


class SessionUpdate(SessionBase):
    pass


class SessionInDBBase(SessionBase):
    id: int
    token: uuid.UUID

    class Config:
        from_attributes = True


class Session(SessionInDBBase):
    pass

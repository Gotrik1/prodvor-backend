from pydantic import BaseModel

class Msg(BaseModel):
    message: str

class Status(BaseModel):
    status: str

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class MessageWithUUID(Message):
    uuid: str

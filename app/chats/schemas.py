from pydantic import BaseModel
from typing import Optional


class ChatBase(BaseModel):
    name: str
    type: str


class ChatCreate(ChatBase):
    created_at: str


class ChatResponse(ChatBase):
    id: int
    created_at: str

    class Config:
        from_attributes  = True

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Базовая схема для сообщения
class MessageBase(BaseModel):
    content: str

# Схема для создания сообщения
class MessageCreate(MessageBase):
    chat_id: int
    sender_id: int
    created_at: Optional[datetime] = None  # Опциональное поле для времени создания

# Схема для вывода сообщения (включает все данные, включая время создания)
class MessageOut(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    sender_username: str
    content: str
    created_at: datetime  # Обязательное поле для времени создания сообщения

    class Config:
        from_attributes = True

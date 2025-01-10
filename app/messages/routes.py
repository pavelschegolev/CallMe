from fastapi import APIRouter, HTTPException, Depends, WebSocket, Cookie, Query
from sqlalchemy.orm import Session
from app.db_connection import get_db
from app.messages import schemas, models
from app.users.models import User
from app.chats.models import Chat
from app.auth.utils import get_current_user
from datetime import datetime
from typing import List
from app.WebSocket import websocket_handler

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

# Словарь для хранения активных WebSocket соединений
active_connections = {}


# 📌 Создание сообщения (POST)
@router.post("/", response_model=schemas.MessageOut)
def create_message(
    message: schemas.MessageCreate, db: Session = Depends(get_db)
):
    if not message.created_at:
        message.created_at = datetime.utcnow()

    db_message = models.Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        content=message.content,
        created_at=message.created_at
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    chat = db.query(Chat).filter(Chat.id == message.chat_id).first()
    if chat:
        chat.last_message_id = db_message.id
        chat.last_message_time = db_message.created_at
        db.commit()

    sender = db.query(User).filter(User.id == db_message.sender_id).first()
    return {
        "id": db_message.id,
        "chat_id": db_message.chat_id,
        "sender_id": db_message.sender_id,
        "sender_username": sender.username if sender else "Unknown",
        "content": db_message.content,
        "created_at": db_message.created_at or datetime.utcnow(),
    }


# 📌 Получение сообщений из чата (GET)
@router.get("/chats/{chat_id}/", response_model=List[schemas.MessageOut])
def get_messages(
        chat_id: int,
        db: Session = Depends(get_db)
):
    messages = (
        db.query(models.Message)
        .join(User, models.Message.sender_id == User.id)
        .filter(models.Message.chat_id == chat_id)
        .order_by(models.Message.created_at)  # Сортировка по убыванию времени
        .all()
    )

    if not messages:
        return []  # Возвращаем пустой список, если сообщений нет

    return [
        {
            "id": message.id,
            "chat_id": message.chat_id,
            "sender_id": message.sender_id,
            "sender_username": message.sender.username,
            "content": message.content,
            "created_at": message.created_at or datetime.utcnow(),
        }
        for message in messages
    ]

# 📌 WebSocket соединение для сообщений
@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
    user_id: int = Cookie(default=None)
):
    if not user_id:
        await websocket.close(code=1008)
        return

    await websocket_handler(websocket, user_id, db)
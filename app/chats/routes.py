from fastapi import APIRouter, Depends,HTTPException, WebSocket
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db_connection import get_db
from app.chats.models import Chat, ChatMember
from app.messages.models import Message
from app.users.models import User
from app.auth.utils import get_current_user
from app.WebSocket import websocket_handler

router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)

@router.websocket("/ws")
async def chat_list_websocket(websocket: WebSocket, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        await websocket.close(code=1008)
        return
    await websocket_handler(websocket, current_user.id, db)


@router.get("/user_chats")
def get_user_chats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user.id

    # Запрашиваем список чатов пользователя с последним сообщением и отправителем
    chats = (
        db.query(
            Chat.id,
            Chat._name.label("chat_name"),
            Chat.is_group,
            Chat.created_at,
            func.coalesce(Message.content, 'No messages yet').label('last_message'),
            func.coalesce(Message.created_at, 'No time available').label('last_message_time'),
            func.coalesce(User.username, 'Unknown').label('last_sender')
        )
        .join(ChatMember, ChatMember.chat_id == Chat.id)  # Соединяем таблицу участников чата
        .outerjoin(
            Message,
            Message.id == db.query(func.max(Message.id))
                .filter(Message.chat_id == Chat.id)
                .correlate(Chat)
                .scalar_subquery()
        )  # Берём последнее сообщение из каждого чата
        .outerjoin(User, User.id == Message.sender_id)  # Берём отправителя последнего сообщения
        .filter(ChatMember.user_id == user_id)  # Фильтруем чаты по user_id
        .order_by(desc(Message.created_at))  # Сортируем по дате последнего сообщения
        .all()
    )

    # Преобразуем результат запроса в список словарей
    result = [
        {
            "id": chat.id,
            "name": chat.chat_name,
            "is_group": chat.is_group,
            "created_at": chat.created_at,
            "last_message": chat.last_message,
            "last_message_time": chat.last_message_time,
            "last_sender": chat.last_sender
        }
        for chat in chats
    ]

    return {"chats": result}

@router.get("/{chat_id}/")
async def get_chat_info(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"id": chat.id, "_name": chat._name, "is_group": chat.is_group}
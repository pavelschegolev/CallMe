import json
from datetime import datetime
from typing import Dict, List, Tuple
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from app.chats.models import Chat
from app.messages import schemas, models
from app.users.models import User

# Хранилище активных соединений: {chat_id: [(user_id, WebSocket), ...]}
active_connections: Dict[int, List[Tuple[int, WebSocket]]] = {}

async def notify_chat_list_update(user_ids: List[int], db):
    """Уведомляет пользователей об изменении в их списке чатов."""
    for user_id in user_ids:
        for chat_id, connections in active_connections.items():
            for connected_user_id, websocket in connections:
                if connected_user_id == user_id:
                    await process_chat_list(websocket, user_id, db, event_type="chat_list_update")

async def process_chat_list(websocket: WebSocket, user_id: int, db, event_type: str = "chat_list"):
    """Обработка события получения или обновления списка чатов."""
    chats = db.query(Chat).filter(Chat.members.any(id=user_id)).all()
    chat_list = [{"chat_id": chat.id, "name": chat._name, "is_group": chat.is_group} for chat in chats]

    response = {"event_type": event_type, "chats": chat_list}
    await websocket.send_text(json.dumps(response))

async def process_chat_message(websocket: WebSocket, data: dict, current_user: User, db):
    """Обработка события отправки сообщения в чат."""
    chat_id = data.get("chat_id")
    content = data.get("content", "").strip()

    if not chat_id or not content:
        error_response = {"event_type": "error", "message": "Invalid chat_id or empty content"}
        await websocket.send_text(json.dumps(error_response))
        return

    # Сохранение сообщения в базу данных
    db_message = models.Message(
        chat_id=chat_id,
        sender_id=current_user.id,
        content=content,
        created_at=datetime.utcnow(),
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    message_data = {
        "event_type": "chat_message",
        "chat_id": chat_id,
        "sender_username": current_user.username,
        "sender_id": current_user.id,
        "content": content,
        "created_at": db_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }
    message_json = json.dumps(message_data)

    # Рассылка сообщения всем участникам чата
    if chat_id in active_connections:
        for _, connection in active_connections[chat_id]:
            await connection.send_text(message_json)

async def websocket_handler(websocket: WebSocket, user_id: int, db):
    """Основной обработчик WebSocket соединения."""
    await websocket.accept()

    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        await websocket.close(code=1008)
        raise HTTPException(status_code=401, detail="User not found")

    # Подключение к чату
    connected_chat_id = None

    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            event_type = data.get("event_type")

            if event_type == "chat_list":
                await process_chat_list(websocket, current_user.id, db)
            elif event_type == "chat_message":
                await process_chat_message(websocket, data, current_user, db)
            elif event_type == "join_chat":
                connected_chat_id = data.get("chat_id")
                if connected_chat_id not in active_connections:
                    active_connections[connected_chat_id] = []
                active_connections[connected_chat_id].append((current_user.id, websocket))
            elif event_type == "update_chat_list":
                # Пример вызова: обновить список чатов для всех указанных пользователей
                user_ids_to_update = data.get("user_ids", [])
                await notify_chat_list_update(user_ids_to_update, db)
            else:
                error_response = {"event_type": "error", "message": f"Unknown event_type: {event_type}"}
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        # Удаляем соединение при разрыве
        if connected_chat_id and connected_chat_id in active_connections:
            active_connections[connected_chat_id] = [
                conn for conn in active_connections[connected_chat_id] if conn[1] != websocket
            ]
            if not active_connections[connected_chat_id]:
                del active_connections[connected_chat_id]

        await websocket.close()

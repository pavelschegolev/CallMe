from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db_connection import get_db
from app.users.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


# Функция для получения текущего пользователя
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")  # Получаем user_id из куки

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_id = int(user_id)  # Преобразуем user_id в int
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID format")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

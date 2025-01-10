from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db_connection import get_db
from app.users.models import User
from app.users.schemas import UserCreate, UserResponse
from app.auth.utils import get_current_user
from passlib.hash import bcrypt


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Хэшируем пароль и создаём пользователя
    hashed_password = bcrypt.hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id}

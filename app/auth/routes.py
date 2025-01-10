from fastapi import APIRouter, Request, Depends, HTTPException, Form, Response, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db_connection import get_db
from app.users.models import User
from app.auth.utils import hash_password, verify_password
import os
import re  # Для валидации email и пароля

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "..", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Страница регистрации (GET)
@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Регистрация пользователя (POST)
@router.post("/register")
async def register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    # Проверка на пустые поля
    if not username or not email or not password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": "Все поля должны быть заполнены"}
        )

    # Проверка формата email
    email_regex = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": "Некорректный формат email"}
        )

    # Проверка на уникальность email
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": "Пользователь с таким email уже существует"}
        )

    hashed_password = hash_password(password)

    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/main_page", status_code=303)

# Страница входа (GET)
@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Авторизация пользователя (POST)
@router.post("/login")
async def login(
        request: Request,
        response: Response,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": "Неправильный email или пароль"}
        )

    response = RedirectResponse(url="/main_page", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response

# Выход пользователя (POST)
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_id")
    return RedirectResponse(url="/auth/login", status_code=303)

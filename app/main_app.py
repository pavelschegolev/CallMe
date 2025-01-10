from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from db_connection import engine, Base, get_db
import uvicorn
import os

from chats.routes import router as chats_router
from auth.routes import router as auth_router
from messages.routes import router as messages_router
from users.routes import router as users_router
# Инициализация БД (создаём таблицы)
Base.metadata.create_all(bind=engine)

# Создаём приложение
app = FastAPI(
    title="Messenger API",
    version="0.1.1",
    debug=True
)
# Абсолютные пути к статическим файлам и шаблонам
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")
JS_DIR = os.path.join(CURRENT_DIR, "JS")

# Настройка для обработки статических файлов
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/JS", StaticFiles(directory=JS_DIR), name="JS")

# Указание директории для шаблонов
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Подключение маршрутов
app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(messages_router)
app.include_router(users_router)



# Middleware для обработки CORS (если нужно)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (изменить в продакшене)
    allow_credentials=True,  # Важно для куки!
    allow_methods=["*"],
    allow_headers=["*"],
)

# Главная страница
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("start_page.html", {"request": request})

# Главная страница чатов
@app.get("/main_page", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})

# Страница ошибки
@app.get("/error", response_class=HTMLResponse)
async def error_page(request: Request):
    return templates.TemplateResponse("error.html", {"request": request})

# Обработчик ошибок 404
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return templates.TemplateResponse("error.html", {"request": request}, status_code=404)


if __name__ == "__main__":
    uvicorn.run("main_app:app", host="127.0.0.1", port=8000, reload=True)
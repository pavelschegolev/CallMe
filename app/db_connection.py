from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# Подключение к MySQL
engine = create_engine(DATABASE_URL)

# Сессия БД для запросов
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()

# Зависимость для FastAPI — получение сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

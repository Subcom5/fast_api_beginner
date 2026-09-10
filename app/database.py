from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Строка подключения к SQLite
DATABSE_URL = "sqlite:///ecommerce.db"

# Создаем Engine (пул соединений)
engine = create_engine(
    DATABSE_URL,
    echo=True                       # включает логирование SQL-запросов в консоль
)

# Создаем фабрику сеансов
SessionLocal = sessionmaker(bind=engine)


# --------------- Асинхронное подключение к PostgreSQL -------------------------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Строка подключения для PostgreSQL
DATABSE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce"

# Создаем Engine (пул соединений)
async_engine = create_async_engine(DATABSE_URL, echo=True)

# Создаем фабрику сеансов
async_session_maker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,     #  отключает «устаревание» (expiration) объектов, хранимых в сессии
    class_= AsyncSession
)



# Определяем базовый класс для моделей
class Base(DeclarativeBase):
    pass

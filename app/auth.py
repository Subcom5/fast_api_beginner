from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.db_depends import get_async_db
from app.models.users import User as UserModel


# Создаёт объект для работы с рекомендуемым алгоритмом хеширования (Argon2)
password_hash = PasswordHash.recommended()

# создаём объект OAuth2, который указывает, что эндпоинт логина находится
# по адресу /users/token.
# FastAPI ожидает токен в заголовке Authorization: Bearer для защищённых эндпоинтов.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_password(password: str) -> str:
    """
    Преобразует пароль в безопасный хэш.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответсвует ли введенный пароль сохраненному хэшу.
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Создает JWT-токен.
    """
    # Создаёт копию входного словаря data, чтобы избежать изменения оригинала.
    # Ожидается, что data содержит ключи, такие как sub (email), role и id
    to_encode = data.copy()

    # Вычисляет время истечения токена (текущая дата + 30 минут) в формате UTC.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Добавляет поле exp (expiration) в payload токена.
    to_encode.update({
        "exp": expire,
        "token_type": "access",
    })

    # Кодирует данные в JWT
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def create_refresh_token(data: dict):
    """
    Создаёт refresh-токен с длительным сроком действия и token_type="refresh".
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

async def get_current_user(
    # Извлекает токен из заголовка запроса с помощью OAuth2PasswordBearer
    token: str = Depends(oauth2_scheme),
    # Получает асинхронную сессию базы данных для выполнения запросов.
    db: AsyncSession = Depends(get_async_db),
):
    """
    Проверяет JWT и возвращает текущего пользователя из БД.
    """
    # Кастомное исключение
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодирует JWT, проверяя его подпись с использованием
        # SECRET_KEY и алгоритма (например, HS256).
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        # Извлекает поле sub (это обычно email) из payload токена.
        email: str | None = payload.get("sub")

        token_type: str | None = payload.get("token_type")

        if email is None or token_type != "access":
            raise credentials_exception

    # Этот блок перехватывает исключение ExpiredSignatureError,
    # которое выбрасывается библиотекой PyJWT, если токен истёк.
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    # базовый класс исключений в библиотеке PyJWT
    except jwt.PyJWTError:
        raise credentials_exception

    user = await db.scalar(
        select(UserModel).where(
            UserModel.email == email,
            UserModel.is_active == True,
        )
    )

    if user is None:
        raise credentials_exception

    return user


async def get_current_seller(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'seller'.
    """
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action"
        )
    return current_user

async def get_current_admin(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'admin'.
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can perform this action"
        )
    return current_user

async def get_current_buyer(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'admin'.
    """

    if current_user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyer can perform this action"
        )
    return current_user

async def get_current_buyer_or_admin(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Проверяет, что пользователь имеет роль 'admin' или 'buyer'.
    """

    if current_user.role not in ("admin", "buyer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyer or admin can perform this action"
        )
    return current_user

# Можно использовать фабрику вместо четырех функций, но я не стал,
# чтобы оставить текущий подход и не править cуществующий код.
def require_roles(*allowed_roles: str):
    async def role_checker(current_user: UserModel = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only {', '.join(allowed_roles)} can perform this action"
            )
        return current_user
    return role_checker

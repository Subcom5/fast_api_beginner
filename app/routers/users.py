import jwt

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from app.models import User as UserModel
from app.schemas import (
    UserCreate,
    User as UserSchema,
    RefreshTokenRequest,
)
from app.db_depends import get_async_db
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.config import SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя с ролью 'buyer' или 'seller'.
    """

    # Проверка уникальности Email
    result = await db.scalar(select(UserModel).where(UserModel.email == user.email))
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registred"
        )

    # Создание объекта пользователя с хэшированным паролем
    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    # Добавление в сессию и сохранение  в БД
    db.add(db_user)
    await db.commit()
    return db_user


@router.post("/token")
async def login(
    # Отвечает за получение данных формы, отправленных в
    # формате application/x-www-form-urlencoded.
    # Класс OAuth2PasswordRequestForm из FastAPI автоматически
    # извлекает из запроса поля username и password.
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Аутенцифицирует пользователя и возвращает JWT с email, role и id.
    """
    user = await db.scalar(
        select(UserModel)
        .where(
            UserModel.email == form_data.username,
            UserModel.is_active == True
        )
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token")
async def refresh_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Обновляет refresh-токен, принимая старый refresh-токен в теле запроса.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    old_refresh_token = body.refresh_token

    try:
        payload = jwt.decode(
            old_refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        # Проверяем, что токен действительно refresh
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        # refresh-токен истек
        raise credentials_exception
    except jwt.PyJWTError:
        # Подпись неверна или  токен поврежден
        raise credentials_exception

    # Проверяем, что пользователь существует и активен
    user = await db.scalar(
        select(UserModel)
        .where(
            UserModel.email == email,
            UserModel.is_active == True
        )
    )
    if user is None:
        raise credentials_exception

    # Генерируем новый refresh-токен
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/access-token")
async def accese_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Обновляет accesse-токен если он просрочен и если не просрочен refresh-токен.
    """
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate refresh token",
    headers={"WWW-Authenticate": "Bearer"},
    )

    current_refresh_token = body.refresh_token

    try:
        payload = jwt.decode(
            current_refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if email is None or token_type != "refresh":
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await db.scalar(
        select(UserModel)
        .where(
            UserModel.email == email,
            UserModel.is_active == True,
        )
    )
    if user is None:
        raise credentials_exception

    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

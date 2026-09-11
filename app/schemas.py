from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from typing import Annotated
from datetime import datetime


class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name: Annotated[
        str,
        Field(
            ...,
            min_length=3,
            max_length=50,
            description="Название категории (3-50 символов)",
        )
    ]
    parent_id: Annotated[
        int | None,
        Field(
            default=None,
            description="ID родительской категории, если есть",
        )
    ]


class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """
    id: Annotated[
        int,
        Field(
            ...,
            description="Уникальный идентификатор категории",
        )
    ]
    name: Annotated[
        str,
        Field(
            ...,
            description="Название категории",
        )
    ]
    parent_id: Annotated[
        int | None,
        Field(
            default=None,
            description="ID родительской категории, если есть",
        )
    ]
    is_active: Annotated[
        bool,
        Field(
            ...,
            description="Активность категории",
        )
    ]

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: Annotated[
        str,
        Field(
            ...,
            min_length=3,
            max_length=100,
            description="Название товара (3-100 символов)",
        )
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            max_length=500,
            description="Описание товара (до 500 символов)",
        )
    ]
    price: Annotated[
        Decimal,
        Field(
            ...,
            gt=0,
            description="Цена товара (больше 0)",
            decimal_places=2,
        )
    ]
    image_url: Annotated[
        str | None,
        Field(
            default=None,
            max_length=200,
            description="URL изображения товара",
        )
    ]
    stock: Annotated[
        int,
        Field(
            ...,
            ge=0,
            description="Количество товара на складе (0 или больше)",
        )
    ]
    category_id: Annotated[
        int,
        Field(
            ...,
            description="ID категории, к которой относится товар",
        )
    ]


class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET запросах.
    """
    id: Annotated[
        int,
        Field(
            ...,
            description="Уникальный идентификатор товара",
        )
    ]
    name: Annotated[
        str,
        Field(
            ...,
            description="Название товара",
        )
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            description="Описание товара",
        )
    ]
    price: Annotated[
        Decimal,
        Field(
            ...,
            description="Цена товара в рублях",
            gt=0,
            decimal_places=2,
        )
    ]
    image_url: Annotated[
        str | None,
        Field(
            default=None,
            description="URL изображения товара",
        )
    ]
    stock: Annotated[
        int,
        Field(
            ...,
            description="Количество товара на складе",
        )
    ]
    category_id: Annotated[
        int,
        Field(
            ...,
            description="ID категории",
        )
    ]
    is_active: Annotated[
        bool,
        Field(
            ...,
            description="Активность товара",
        )
    ]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Модель для создания и обновления пользователя.
    Используется в POST и PUT запросах.
    """
    email: Annotated[
        EmailStr,
        Field(
            ...,
            description="Email пользователя",
        )
    ]
    password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            description="Пароль (минимум 8 символов)",
        )
    ]
    role: Annotated[
        str,
        Field(
            default="buyer",
            pattern="^(buyer|seller|admin)$",
            description="Роль: 'buyer', 'admin' или 'seller'",
        )
    ]


class User(BaseModel):
    """
    Модель для ответа с данными пользователя.
    Ипользуется в GET запросах.
    """
    id: Annotated[
        int,
        Field(
            ...,
            description="Уникальный идентификатор пользователя",
        )
        ]
    email: Annotated[
        EmailStr,
        Field(
            ...,
            description="Email пользователя",
        )
    ]
    is_active: Annotated[
        bool,
        Field(
            ...,
            description="Активность пользователя",
        )
    ]
    role: Annotated[
        str,
        Field(
            ...,
            description="Роль пользователя (продавец, покупатель, админ)",
        )
    ]

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    """
    Модель для ответа с данными refresh-токена.
    """
    refresh_token: Annotated[
        str,
        Field(
            ...,
            description="Refresh-токен"
        )
    ]

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    """
    Модель для создания и обновления отзыва.
    Используется в POST и PUT запросах.
    """
    comment: Annotated[
        str | None,
        Field(
            max_length=1000,
            default=None,
            description="Текст комментария",
        )
    ]
    grade: Annotated[
        int,
        Field(
            ...,
            ge=1,
            le=5,
            description="Оценка товара (от 1 до 5)",
        )
    ]

class Review(BaseModel):
    """
    Модель для ответа с данными отзыва.
    Используется в GET запросах.
    """
    id: Annotated[
        int,
        Field(
            description="Уникальный идентификатор отзыва",
        )
    ]
    user_id: Annotated[
        int,
        Field(
            description="Уникальный идентификатор покупателя",
        )
    ]
    product_id: Annotated[
        int,
        Field(
            description="Уникальный идентификатор продукта",
        )
    ]
    comment: Annotated[
        str | None,
        Field(
            max_length=1000,
            description="Текст отзыва",
        )
    ]
    comment_date: Annotated[
        datetime,
        Field(
            description="Дата отзыва",
        )
    ]
    grade: Annotated[
        int,
        Field(
            ge=1,
            le=5,
            description="Оценка товара (от 1 до 5)",
        )
    ]
    is_active: Annotated[
        bool,
        Field(
            description="Активность отзыва",
        )
    ]

    model_config = ConfigDict(from_attributes=True)

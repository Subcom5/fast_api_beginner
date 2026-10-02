from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import Product
    from app.models import Review
    from app.models import CartItem
    from app.models import Order


class User(Base):
    """
    Модель таблицы БД "Пользователи"
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор пользователя"
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Адрес электронной почты"
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Захэшированный пароль"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default= True,
        comment="Метка активности пользователя"
    )
    role: Mapped[str] = mapped_column(
        String,
        default="buyer",
        comment="Роль пользователя"
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="seller",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
    )
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )

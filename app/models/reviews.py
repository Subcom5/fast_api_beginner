from sqlalchemy import (
    Boolean, Integer, String, Text, DateTime,
    func, CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.database import Base
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import User
    from app.models import Product


class Review(Base):
    """
    Модель таблицы БД "Отзывы"
    """
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор отзыва"
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        comment="Уникальный идентификатор пользователя из таблицы users"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        comment="Уникальный идентификатор продукта из таблицы products")
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Текст отзыва"
    )
    comment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата и время отзыва"
    )
    grade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Оценка товара покупателем"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Метка активности отзыва"
    )

    __table_args__ = (
        CheckConstraint("grade BETWEEN 1 AND 5", name="ck_review_grade"),
    )

    user: Mapped["User"]  = relationship(
        "User",
        back_populates="reviews",
     )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="reviews",
    )

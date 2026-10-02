from decimal import Decimal

from sqlalchemy import (
    Integer, String, Boolean, Numeric, func,
    Computed, Index,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from datetime import date

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import Category
    from app.models import User
    from app.models import Review
    from app.models import CartItem
    from app.models import OrderItem


class Product(Base):
    """
    Модель таблицы БД "Продукция"
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор продукта"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Название товара"
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Описание товара"
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Стоимость товара"
    )
    image_url: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Фотография товара"
    )
    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Количество товара"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Метка активности товара"
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        comment="Уникальный идентификатор категории товара из таблицы categories"
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        comment="Уникальный идентификатор продавца товара из таблицы users"
    )
    rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 1),
        default=Decimal(0.0),
        server_default="0",
        nullable=False,
        comment="Рейтинг товара"
    )
    tsv: Mapped[TSVECTOR] = mapped_column(
            TSVECTOR,
            Computed(
            """
            setweight(to_tsvector('english', coalesce(name, '')), 'A')
            ||
            setweight(to_tsvector('english', coalesce(description, '')), 'B')
            """,
            persisted=True,
        )
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
    )
    seller: Mapped["User"] = relationship(
        "User",
        back_populates="products",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="product",
    )
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product"
    )

    __table_args__ = (
        Index("ix_products_tsv_gin", "tsv", postgresql_using="gin"),
    )

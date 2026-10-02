from decimal import Decimal
from datetime import datetime
from sqlalchemy import Integer, String, Numeric, DateTime, func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import User, Product


class Order(Base):
    """
    Модель таблицы БД "Заказы"
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор заказа"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Уникальный идентификатор пользователя из таблицы users"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        comment="Статус заказа"
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Общая сумма заказа"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Время создания заказа"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Время обновления заказа"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="orders"
    )
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """Модель таблицы БД "Информация по одному товару в заказе" """
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный номер товара в заказе"
    )
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Уникальный номер заказа из таблицы orders"
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
        comment="Уникальный номер заказа из таблицы products"
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Количество единиц одного вида товара"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Стоимомсть одного товара"
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Общая стоимость товара"
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items"
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="order_items"
    )

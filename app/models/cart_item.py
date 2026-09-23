from datetime import datetime
from sqlalchemy import (
    DateTime, ForeignKey, Integer, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import User
    from app.models import Product


class CartItem(Base):
    """
    Модель таблицы БД "Корзина"
    """
    __tablename__ = "cart_item"

    __table_args__ = (
        UniqueConstraint("user_id", "product_id",
            name="uq_cart_items_user_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Уникальный идентификатор владельца корзины из таблицы users"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Уникальный идентификатор продукта из таблицы product"
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Количество единиц одного товара в корзине"
    )
    created_add: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Метка времени создания записи"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_onupdate=func.now(),
        nullable=False,
        comment="Метка времени последнего обновления записи"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="cart_items"
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="cart_items"
    )

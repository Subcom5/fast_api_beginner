from sqlalchemy import Integer, String, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import Product


class Category(Base):
    """
    Модель таблицы БД "Категории товаров"
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор категории товаров"
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Название категории товара"
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
        comment="Уникальный идентификатор родительской категории товара"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Метка активности категории"
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category"
    )

    parent: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="children",
        # remote_side - необходим для самоссылающихся связей,
        # чтобы SQLAlchemy понимал, что parent_id ссылается на id той же таблицы.
        remote_side="Category.id"
    )

    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent"
    )

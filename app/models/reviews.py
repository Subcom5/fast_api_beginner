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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

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

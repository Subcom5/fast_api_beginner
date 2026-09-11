from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import Product as ProductModel
from app.models import User as UserModel
from app.models import Review as ReviewModel
from app.schemas import ReviewCreate, Review as ReviewSchema
from app.db_depends import get_async_db
from app.auth import get_current_buyer, get_current_buyer_or_admin


router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


async def update_product_rating(
    product_id: int, db: AsyncSession):
    """
    Функция для пересчета среднего рейтинга продукта
    """
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating: Decimal | None = result.scalar()
    if avg_rating is None:
        avg_rating = Decimal("0.0")

    product = await db.get(ProductModel, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found")

    product.rating = avg_rating


@router.get("/", response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех отзывов о товарах.
    """
    stmt = select(ReviewModel).where(ReviewModel.is_active == True)
    reviews = await db.scalars(stmt)
    return reviews.all()


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    product_id: int,
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer),
):
    """
    Создает новый отзыв о товаре
    """
    stmt_product = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True,
    )
    db_product = await db.scalar(stmt_product)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )

    db_review = ReviewModel(
        **review.model_dump(),
        user_id = current_user.id,
        product_id = db_product.id,
    )
    db.add(db_review)
    await update_product_rating(db_product.id, db)
    await db.commit()
    await db.refresh(db_review)

    return db_review


@router.get(
    "/products/{product_id}/reviews",
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK
)
async def get_product_reviews(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Возвращает список всех отзывов о товаре.
    """
    stmt_product = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True,
    )
    db_product = await db.scalar(stmt_product)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )

    stmt_reviews = select(ReviewModel).where(
        ReviewModel.product_id == product_id,
        ReviewModel.is_active == True,
    )
    result = await db.scalars(stmt_reviews)
    db_review = result.all()
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The product has no reviews."
        )
    return db_review


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer_or_admin)
):
    """
    Удаление отзыва по его ID
    """
    stmt = select(ReviewModel).where(
        ReviewModel.id == review_id,
        ReviewModel.is_active == True,
    )
    db_review = await db.scalar(stmt)
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or inactive",
        )

    if current_user.role != "admin" and current_user.id != db_review.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author or admin can delete a review.",
        )

    await db.execute(
        update(ReviewModel)
        .where(ReviewModel.id == review_id)
        .values(is_active=False)
    )
    await update_product_rating(db_review.product_id, db)
    await db.commit()

    return {"message": "Review deleted"}

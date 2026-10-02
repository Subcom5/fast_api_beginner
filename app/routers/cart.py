from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.db_depends import get_async_db
from app.models import (
    CartItem as CartItemModel,
    Product as ProductModel,
    User as UserModel,
)
from app.schemas import (
    Cart as CartSchema,
    CartItem as CartItemSchema,
    CartItemCreate,
    CartItemUpdate,
)


router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)

async def _ensure_product_available(
    db: AsyncSession, product_id: int
) -> None:
    """
    Функция проверяет, что товар с указанным product_id существет в БД,
    активен и доступен для добавления в корзину.
    """
    result = await db.scalars(
        select(ProductModel)
        .where(
            ProductModel.id == product_id,
            ProductModel.is_active == True,
        )
    )
    product = result.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )

async def _get_cart_item(
    user_id: int,
    product_id: int,
    db: AsyncSession
) -> CartItemModel | None:
    """
    Функция ищет товар в корзине текущего пользователя по product_id.
    """
    result = await db.scalars(
        select(CartItemModel)
        .options(selectinload(CartItemModel.product))
        .where(
            CartItemModel.user_id == user_id,
            CartItemModel.product_id == product_id,
        )
    )
    return result.first()


@router.get("/", response_model=CartSchema)
async def get_cart(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Получение данных корзины пользователя
    """
    result = await db.scalars(
        select(CartItemModel)
        .options(selectinload(CartItemModel.product))
        .where(CartItemModel.user_id == current_user.id)
        .order_by(CartItemModel.id)
    )
    items = result.all()

    total_quantity = sum(item.quantity for item in items)
    price_items = (
        Decimal(item.quantity) *
        (item.product.price if item.product.price is not None else Decimal("0"))
        for item in items
    )
    total_price_decimal = sum(price_items, Decimal("0.00"))

    return CartSchema(
        user_id=current_user.id,
        items=items,                        # type: ignore[arg-type]
        total_quantity=total_quantity,
        total_price=total_price_decimal
    )


@router.post(
    "/items",
    response_model=CartItemSchema,
    status_code=status.HTTP_201_CREATED
)
async def add_item_to_cart(
    payload: CartItemCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Добавляет товар в корзину пользователя или увеличивает его количество,
    если он уже есть.
    """
    await _ensure_product_available(db, payload.product_id)

    cart_item = await _get_cart_item(current_user.id, payload.product_id, db)
    if cart_item:
        cart_item.quantity += payload.quantity
    else:
        cart_item = CartItemModel(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity
        )
        db.add(cart_item)

    await db.commit()
    update_item = await _get_cart_item(current_user.id, payload.product_id, db)
    return update_item


@router.put("/items/{product_id}", response_model=CartItemSchema)
async def update_cart_item(
    product_id: int,
    payload: CartItemUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Обновляет количество товара в корзине пользователя
    """
    await _ensure_product_available(db, product_id)

    cart_item = await _get_cart_item(current_user.id, product_id, db)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    cart_item.quantity = payload.quantity
    await db.commit()
    updated_item = await _get_cart_item(current_user.id, product_id, db)

    return updated_item


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
):
    cart_item = await _get_cart_item(current_user.id, product_id, db)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    await db.delete(cart_item)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
):
    await db.execute(
        delete(CartItemModel)
        .where(CartItemModel.user_id == current_user.id)
    )
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

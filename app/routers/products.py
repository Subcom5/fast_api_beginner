from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category as CategoryModel
from app.models import Product as ProductModel
from app.models import User as UserModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_async_db
from app.auth import get_current_seller


# Создаем маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    result = await db.scalars(stmt)
    products = result.all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Создает новый товар, привязанный к текущему продавцу(только для "seller").
    """
    # Проверка существования category_id
    stmt = select(CategoryModel).where(
        CategoryModel.id == product.category_id,
        CategoryModel.is_active == True
    )
    db_category = await db.scalar(stmt)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or inactive"
        )
    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)    # Для получения id и is_active из базы
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Возвращает список товаров в указанной категории по ее ID.
    """
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True
    )
    db_category = await db.scalar(stmt)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or inactive"
        )
    stmt_product= select(ProductModel).where(
        ProductModel.category_id == category_id,
        ProductModel.is_active == True
    )
    result = await db.scalars(stmt_product)
    db_product = result.all()
    return db_product


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    )
    db_product = await db.scalar(stmt)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )

    stmt_category = select(CategoryModel).where(
        CategoryModel.id == db_product.category_id,
        CategoryModel.is_active == True
    )
    db_category = await db.scalar(stmt_category)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or inactive"
        )
    return db_product

@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(
        product_id: int,
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller)
    ):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    stmt = select(ProductModel).where(
    ProductModel.id == product_id,
    ProductModel.is_active == True
    )
    db_product = await db.scalar(stmt)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found or inactive"
        )

    if db_product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products",
        )

    stmt_category = select(CategoryModel).where(
        CategoryModel.id == db_product.category_id,
        CategoryModel.is_active == True
    )
    db_category = await db.scalar(stmt_category)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found or inactive"
        )
    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Выполняет мягкое удаление товара,
    если он принадлежит текущему продавцу (только для 'seller').
    """
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    )
    db_product = await db.scalar(stmt)

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactiv"
        )
    if db_product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own products"
        )

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(is_active=False)
    )
    await db.commit()
    await db.refresh(db_product)
    return db_product

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category as CategoryModel
from app.models import User as UserModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db
from app.db_depends import get_async_db
from app.auth import get_current_admin


# Создаем маршрутизатор с префиксом и тегом
router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех категорий товаров.
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    categories = result.all()
    return categories


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin)
):
    """
    Создает новую категорию.
    """
    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == category.parent_id,
            CategoryModel.is_active == True
        )
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )

    # Создание новой категории
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    return db_category


@router.put("/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin),
):
    """
    Обновляет категорию по ее ID.
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True
    )
    result = await db.scalars(stmt)
    db_category = result.first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catogory not found"
        )

    # Проверка существования parent_id если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(
            CategoryModel.id == category.parent_id,
            CategoryModel.is_active == True
        )
        parent_result = await db.scalars(parent_stmt)
        parent = parent_result.first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent catogory not found"
            )
        if parent.id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent catogory not found"
            )

    # Обновление категории
    update_data = category.model_dump(exclude_unset=True) # True - обновляет только переданные поля
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**update_data)
    )
    await db.commit()
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int, db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin),
):
    """
    Выполняет мягкое удаление категории по ее ID, устанавливая is_active=False.
    """
    # Проверка существования активной категории
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True
    )
    result = await db.scalars(stmt)
    db_category = result.first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Логическое удаление категории (установка is_active=False)
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    await db.commit()
    return db_category

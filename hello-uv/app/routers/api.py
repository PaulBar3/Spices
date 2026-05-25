from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_session
from app.models.product import Product, ProductCreate, ProductUpdate

router = APIRouter(prefix="/api", tags=["products"])


@router.get("/products")
async def get_products(session: AsyncSession = Depends(get_session)) -> List[Product]:
    """Получение списка всех товаров"""
    result = await session.execute(select(Product))
    products = result.scalars().all()
    return list(products)


@router.get("/products/{product_id}")
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)) -> Product:
    """Получение одного товара по ID"""
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    return product


@router.post("/products")
async def create_product(product_data: ProductCreate, session: AsyncSession = Depends(get_session)) -> Product:
    """Создание нового товара"""
    product = Product.model_validate(product_data)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    session: AsyncSession = Depends(get_session)
) -> Product:
    """Обновление товара"""
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.delete("/products/{product_id}")
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    """Удаление товара"""
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    await session.delete(product)
    await session.commit()
    
    return {"message": "Товар успешно удален"}

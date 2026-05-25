from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_session
from app.models.product import Product, ProductCreate, ProductUpdate
from starlette.templating import Jinja2Templates

router = APIRouter()


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.templates


@router.get("/", name="home")
async def home(request: Request, session: AsyncSession = Depends(get_session)):
    """Главная страница со списком товаров"""
    result = await session.execute(select(Product))
    products = result.scalars().all()
    templates = get_templates(request)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "products": products}
    )


@router.get("/product/{product_id}", name="product_detail")
async def product_detail(request: Request, product_id: int, session: AsyncSession = Depends(get_session)):
    """Страница детального просмотра товара"""
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    templates = get_templates(request)
    return templates.TemplateResponse(
        "product_detail.html",
        {"request": request, "product": product}
    )


@router.get("/admin", name="admin")
async def admin_panel(request: Request, session: AsyncSession = Depends(get_session)):
    """Админ панель со списком товаров для редактирования"""
    result = await session.execute(select(Product))
    products = result.scalars().all()
    templates = get_templates(request)
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "products": products}
    )


@router.get("/admin/product/create", name="product_create")
async def product_create_form(request: Request):
    """Форма создания товара"""
    templates = get_templates(request)
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "product": None, "action": "/admin/product/create"}
    )


@router.post("/admin/product/create")
async def product_create(
    request: Request,
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_session)
):
    """Создание нового товара"""
    product = Product.model_validate(product_data)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    
    result = await session.execute(select(Product))
    products = result.scalars().all()
    templates = get_templates(request)
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "products": products, "message": "Товар успешно создан"}
    )


@router.get("/admin/product/{product_id}/edit", name="product_edit")
async def product_edit_form(request: Request, product_id: int, session: AsyncSession = Depends(get_session)):
    """Форма редактирования товара"""
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    templates = get_templates(request)
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "product": product, "action": f"/admin/product/{product_id}/edit"}
    )


@router.post("/admin/product/{product_id}/edit")
async def product_edit(
    request: Request,
    product_id: int,
    product_data: ProductUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Редактирование товара"""
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
    
    result = await session.execute(select(Product))
    products = result.scalars().all()
    templates = get_templates(request)
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "products": products, "message": "Товар успешно обновлен"}
    )


@router.post("/admin/product/{product_id}/delete", name="product_delete")
async def product_delete(
    request: Request,
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Удаление товара"""
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    await session.delete(product)
    await session.commit()
    
    result = await session.execute(select(Product))
    products = result.scalars().all()
    templates = get_templates(request)
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "products": products, "message": "Товар успешно удален"}
    )

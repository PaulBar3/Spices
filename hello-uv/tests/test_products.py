import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_session, SQLModel, engine

@pytest.fixture(scope="function")
async def test_db():
    """Создание тестовой базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(test_db):
    """Тестовый клиент"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_get_products_empty(client):
    """Тест получения пустого списка товаров"""
    response = await client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert data == []

@pytest.mark.asyncio
async def test_create_product(client):
    """Тест создания товара"""
    product_data = {
        "name": "Test Product",
        "description": "Test Description",
        "price": 99.99
    }
    response = await client.post("/api/products", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["description"] == "Test Description"
    assert data["price"] == 99.99
    assert "id" in data

@pytest.mark.asyncio
async def test_get_product(client):
    """Тест получения одного товара"""
    # Создаем товар
    product_data = {
        "name": "Single Product",
        "description": "Single Description",
        "price": 49.99
    }
    create_response = await client.post("/api/products", json=product_data)
    product_id = create_response.json()["id"]
    
    # Получаем товар
    response = await client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Product"
    assert data["id"] == product_id

@pytest.mark.asyncio
async def test_update_product(client):
    """Тест обновления товара"""
    # Создаем товар
    product_data = {
        "name": "Update Product",
        "description": "Original Description",
        "price": 29.99
    }
    create_response = await client.post("/api/products", json=product_data)
    product_id = create_response.json()["id"]
    
    # Обновляем товар
    update_data = {
        "name": "Updated Product",
        "description": "Updated Description",
        "price": 39.99
    }
    response = await client.put(f"/api/products/{product_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["description"] == "Updated Description"
    assert data["price"] == 39.99

@pytest.mark.asyncio
async def test_delete_product(client):
    """Тест удаления товара"""
    # Создаем товар
    product_data = {
        "name": "Delete Product",
        "description": "To be deleted",
        "price": 19.99
    }
    create_response = await client.post("/api/products", json=product_data)
    product_id = create_response.json()["id"]
    
    # Удаляем товар
    response = await client.delete(f"/api/products/{product_id}")
    assert response.status_code == 200
    
    # Проверяем, что товар удален
    get_response = await client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_product_not_found(client):
    """Тест получения несуществующего товара"""
    response = await client.get("/api/products/9999")
    assert response.status_code == 404

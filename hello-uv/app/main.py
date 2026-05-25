from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from contextlib import asynccontextmanager
from pathlib import Path

from app.database import init_db
from app.routers import products
from app.routers import api


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация приложения"""
    # Инициализация базы данных при старте
    await init_db()
    yield
    # Очистка при остановке (если нужно)


app = FastAPI(
    title="Магазин товаров",
    description="Асинхронное приложение для управления товарами",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка шаблонов и статических файлов
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.templates = templates

# Монтирование статических файлов
static_path = BASE_DIR / "templates" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Подключение роутеров
app.include_router(products.router)
app.include_router(api.router)


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "ok"}

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.config import settings
from app.db import init_db, close_db
from app.i18n.core import _load_translations
from app.middleware.i18n import I18nMiddleware
from app.routes.user import router as user_router
from app.utils.valkey import close_valkey
from app.utils.queue import close_queue


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    _load_translations()
    await init_db()
    yield
    # Shutdown
    await close_db()
    await close_queue()
    await close_valkey()


app = FastAPI(
    title=settings.APP_NAME,
    description="API for AI-powered code review agent with user management, "
    "internationalization, and caching.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Middleware
app.add_middleware(I18nMiddleware)

# Routes
app.include_router(user_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

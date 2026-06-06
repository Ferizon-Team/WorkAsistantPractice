from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.v1.routers import main_router

from src.logger import logger

from src.api.middleware import log_middleware

from src.core.database import database
from src.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    yield
    logger.info("Shutdown API...")
    await database.dispose_engine()

app = FastAPI(lifespan=lifespan)
app.include_router(main_router)

app.add_middleware(BaseHTTPMiddleware, dispatch = log_middleware)



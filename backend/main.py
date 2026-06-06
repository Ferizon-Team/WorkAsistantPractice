from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware

from src.service.rag_service import RAGService
from src.service.embedding_model_service import embedding_service
from src.repository.document.search_repository import search_repository
from src.repository.document.document_repository import document_repository
from src.service.llm_client_service import llm_client
from src.api.routers import main_router

from src.logger import logger

from src.api.middleware import log_middleware

from src.core.database import database
from src.core.config import settings
from src.service.model_manager_service import ModelManager
from src.service.tts_service import TTSService

model_manager = ModelManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")

    if not await llm_client.check_health():
        await llm_client.pull_model()
    app.state.rag_service = RAGService(
        embedding_service = embedding_service,
        llm_client = llm_client,
        search_repository = search_repository,
        document_repository = document_repository
        )
    
    tts_model = model_manager.get_tts_model()
    app.state.tts_service = TTSService(
        model=tts_model,
        output_dir="storage/tts",
        audio_format="wav",
    )

    yield

    logger.info("Shutdown API...")
    await database.dispose_engine()

app = FastAPI(lifespan=lifespan)
app.include_router(main_router)

app.add_middleware(BaseHTTPMiddleware, dispatch = log_middleware)



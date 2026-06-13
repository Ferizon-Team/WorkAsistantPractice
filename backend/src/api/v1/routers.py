from fastapi import APIRouter
from src.api.v1.document import router as document_router
from src.api.v1.tts import router as tts_router
from src.api.v1.stt import router as stt_router

main_router = APIRouter(prefix="/v1")

main_router.include_router(document_router)
main_router.include_router(tts_router)
main_router.include_router(stt_router)
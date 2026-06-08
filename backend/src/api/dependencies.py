from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from redis.asyncio import Redis as AsyncRedis

from src.core.database import database
from src.service.rag_service import RAGService
from src.service.stt_service import STTService
from src.service.tts_service import TTSService
from src.core.cache import get_redis_client

def get_rag_service(request : Request) -> RAGService:
    return request.app.state.rag_service

def get_tts_service(request: Request) -> TTSService:
    return request.app.state.tts_service

def get_stt_service(request: Request) -> STTService:
    return request.app.state.stt_service
  
  
SessionDep = Annotated[AsyncSession, Depends(database.get_session)]
RedisDep = Annotated[AsyncRedis, Depends(get_redis_client)]
RagServiceDep = Annotated[RAGService, Depends(get_rag_service)]
STTServiceDep = Annotated[STTService, Depends(get_stt_service)]
TTSServiceDep = Annotated[TTSService, Depends(get_tts_service)]

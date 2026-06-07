from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from src.core.database import database
from src.service.rag_service import RAGService
from src.service.stt_service import STTService
from src.service.tts_service import TTSService

def get_rag_service(request : Request) -> RAGService:
	return request.app.state.rag_service

def get_tts_service(request: Request) -> TTSService:
    return request.app.state.tts_service

def get_stt_service(request: Request) -> STTService:
    return request.app.state.stt_service
  
  
SessionDep = Annotated[AsyncSession, Depends(database.get_session)]
RagServiceDep = Annotated[RAGService, Depends(get_rag_service)]
STTServiceDep = Annotated[STTService, Depends(get_stt_service)]
TTSServiceDep = Annotated[TTSService, Depends(get_tts_service)]

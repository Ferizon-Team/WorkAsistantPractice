from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from src.core.database import database
from src.service.rag_service import RAGService


def get_rag_service(request : Request) -> RAGService:
	return request.app.state.rag_service

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]
RagServiceDep = Annotated[RAGService, Depends(get_rag_service)]
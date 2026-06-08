from fastapi import APIRouter, Query
from src.api.dependencies import SessionDep, RagServiceDep, TTSServiceDep, STTServiceDep
from src.schemas.document import LoadDocument
from src.schemas.rag import AnswerQuestionResponse


router = APIRouter(prefix = "/document")




@router.post("/")
async def load_document(
        new_document: LoadDocument,
        db_session : SessionDep,
        rag_service: RagServiceDep,
        ) -> int:

    loaded_document = await rag_service.load_document(
        session=db_session,
        title = new_document.title,
        text = new_document.text,
        category = new_document.category,
        )

    return loaded_document

@router.get("/request")
async def send_request(
        db_session : SessionDep,
        rag_service: RagServiceDep,
        tts_service: TTSServiceDep,
        stt_service: STTServiceDep,
        question : str = Query(...),

        ) -> AnswerQuestionResponse:

    answer = await rag_service.answer_question(
        session=db_session,
        question = question,
        category = None

        )

    return answer






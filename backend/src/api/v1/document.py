from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from src.api.dependencies import SessionDep, RagServiceDep, CacheDep
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
        redis_connect : CacheDep,
        rag_service: RagServiceDep,
        question : str = Query(...),

        ) -> AnswerQuestionResponse:

    answer = await rag_service.answer_question(
        redis_connect = redis_connect,
        session=db_session,
        question = question,
        category = None

        )

    return answer

@router.websocket("/ws")
async def websocket_endpoint(
        websocket : WebSocket,
        db_session : SessionDep,
        redis_connect : CacheDep,
        rag_service: RagServiceDep,
        ):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            if data.get('event') == "question":
                async for chunk in rag_service.answer_question_stream(
                    redis_connect = redis_connect,
                    session = db_session,
                    question = data.get('question'),
                    category = None
                        ):

                    await websocket.send_json(chunk.model_dump_json())

    except WebSocketDisconnect:
        await websocket.close()









from fastapi import APIRouter
from src.api.dependencies import SessionDep, RagServiceDep
from src.schemas.document import LoadDocument


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






from fastapi import APIRouter
from src.api.dependencies import SessionDep
from src.repository.user import UserRepository


router = APIRouter()




@router.get("/")
async def root(session : SessionDep):
    return "Hello World!"





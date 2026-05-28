from fastapi import APIRouter
from src.api.v1.root import router as root_router

main_router = APIRouter()

main_router.include_router(root_router)

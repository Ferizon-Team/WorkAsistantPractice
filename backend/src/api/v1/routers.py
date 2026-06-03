from fastapi import APIRouter
from src.api.v1.document import router as root_router

main_router = APIRouter(prefix = "/v1")

main_router.include_router(root_router)

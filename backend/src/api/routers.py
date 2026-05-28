from fastapi import APIRouter
from api.v1.root import router as root_router

main_router = APIRouter()

main_router.include_router(root_router)


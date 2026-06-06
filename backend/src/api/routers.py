from fastapi import APIRouter
from src.api.v1.routers import main_router as main_router_v1

main_router = APIRouter(prefix = "/api")

main_router.include_router(main_router_v1)


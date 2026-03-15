from fastapi import APIRouter

from .auth.router import router as auth_router
from .links.router import router as links_router

api_router = APIRouter()
api_router.include_router(
    auth_router,
)
api_router.include_router(
    links_router,
)

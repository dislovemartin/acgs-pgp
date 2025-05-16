from fastapi import APIRouter
from .endpoints import synthesize

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    synthesize.router,
    prefix="/synthesize",
    tags=["synthesize"]
)

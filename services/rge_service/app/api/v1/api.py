from fastapi import APIRouter
from .endpoints import evaluate

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    evaluate.router, 
    prefix="/evaluate", 
    tags=["evaluation"]
)

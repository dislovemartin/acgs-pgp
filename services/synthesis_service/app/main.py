import logging
import sys
import os
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import the common schemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from .core.config import settings
from .db.session import Base, engine, get_db
from .api.v1.api import api_router
from .models.policy import PolicyModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("synthesis-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Initialize any required services here
    logger.info("Initializing services...")

    yield

    # Clean up resources on shutdown
    logger.info("Shutting down services...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Synthesis Service for ACGS-PGP",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "0.1.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.pool import QueuePool
import os
from ..core.config import settings

# Use the database URL from settings
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

# Create the SQLAlchemy engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.SQL_ECHO
)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

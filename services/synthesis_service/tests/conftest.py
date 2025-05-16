import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Skip database creation for schema validation tests
# Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override the get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency in the app
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def db_session():
    """Create a database session for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Skip database cleanup for schema validation tests
        # Base.metadata.drop_all(bind=engine)
        # Base.metadata.create_all(bind=engine)

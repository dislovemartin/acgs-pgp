import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import json
import sys
import os

# Add the parent directory to the path so we can import the common schemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from common.schemas.constitution import (
    AIConstitution, AIConstitutionCreate, AIConstitutionUpdate,
    AIConstitutionPrinciple
)

# Import the app and models
from app.main import app
from app.models.constitution import AIConstitutionModel
from app.crud import constitution as crud_constitution

# Create test client
client = TestClient(app)

# Test data
TEST_TIMESTAMP = datetime.now(timezone.utc)
TEST_ID = "550e8400-e29b-41d4-a716-446655440000"

@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    with patch("app.db.base.get_db") as mock_get_db:
        mock_session = MagicMock()
        mock_get_db.return_value = mock_session
        yield mock_session

@pytest.fixture
def test_constitution():
    """Create a test constitution for testing."""
    return AIConstitution(
        id=TEST_ID,
        version=1,
        title="Test Constitution",
        description="Test constitution description",
        principles=[
            AIConstitutionPrinciple(
                article_id="test.1",
                title="Test Principle",
                description="Test principle description",
                category="test",
                keywords=["test"],
                examples=["Test example"],
                related_articles=[]
            )
        ],
        categories=["test"],
        metadata={"test": "test"},
        created_at=TEST_TIMESTAMP,
        updated_at=TEST_TIMESTAMP,
        created_by="test-user",
        updated_by="test-user"
    )

@pytest.fixture
def test_constitution_model(test_constitution):
    """Create a test constitution model for testing."""
    model = AIConstitutionModel(
        id=test_constitution.id,
        version=test_constitution.version,
        title=test_constitution.title,
        description=test_constitution.description,
        principles=[principle.dict() for principle in test_constitution.principles],
        categories=test_constitution.categories,
        metadata_=test_constitution.metadata,
        created_at=test_constitution.created_at,
        updated_at=test_constitution.updated_at,
        created_by=test_constitution.created_by,
        updated_by=test_constitution.updated_by
    )
    model.to_dict = lambda: test_constitution.dict()
    return model

def test_create_constitution(mock_db_session, test_constitution):
    """Test creating a constitution."""
    # Mock the CRUD operation
    with patch.object(crud_constitution, "create_constitution") as mock_create:
        mock_create.return_value = test_constitution
        
        # Create request data
        request_data = AIConstitutionCreate(
            title="Test Constitution",
            description="Test constitution description",
            principles=[
                AIConstitutionPrinciple(
                    article_id="test.1",
                    title="Test Principle",
                    description="Test principle description"
                )
            ],
            created_by="test-user",
            updated_by="test-user"
        ).dict()
        
        # Make the request
        response = client.post("/api/v1/constitution", json=request_data)
        
        # Assert the response
        assert response.status_code == 201
        assert response.json()["id"] == TEST_ID
        assert response.json()["title"] == "Test Constitution"
        assert len(response.json()["principles"]) == 1
        
        # Verify the mock was called
        mock_create.assert_called_once()

def test_get_constitutions(mock_db_session, test_constitution_model):
    """Test getting all constitutions."""
    # Mock the CRUD operation
    with patch.object(crud_constitution, "get_constitutions") as mock_get:
        mock_get.return_value = [test_constitution_model]
        
        # Make the request
        response = client.get("/api/v1/constitution")
        
        # Assert the response
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == TEST_ID
        assert response.json()[0]["title"] == "Test Constitution"
        
        # Verify the mock was called
        mock_get.assert_called_once_with(mock_db_session, skip=0, limit=100)

def test_get_latest_constitution(mock_db_session, test_constitution_model):
    """Test getting the latest constitution."""
    # Mock the CRUD operation
    with patch.object(crud_constitution, "get_latest_constitution") as mock_get:
        mock_get.return_value = test_constitution_model
        
        # Make the request
        response = client.get("/api/v1/constitution/latest")
        
        # Assert the response
        assert response.status_code == 200
        assert response.json()["id"] == TEST_ID
        assert response.json()["title"] == "Test Constitution"
        
        # Verify the mock was called
        mock_get.assert_called_once_with(mock_db_session)

def test_get_constitution(mock_db_session, test_constitution_model):
    """Test getting a specific constitution."""
    # Mock the CRUD operation
    with patch.object(crud_constitution, "get_constitution") as mock_get:
        mock_get.return_value = test_constitution_model
        
        # Make the request
        response = client.get(f"/api/v1/constitution/{TEST_ID}")
        
        # Assert the response
        assert response.status_code == 200
        assert response.json()["id"] == TEST_ID
        assert response.json()["title"] == "Test Constitution"
        
        # Verify the mock was called
        mock_get.assert_called_once_with(mock_db_session, constitution_id=TEST_ID)

def test_get_constitution_not_found(mock_db_session):
    """Test getting a constitution that doesn't exist."""
    # Mock the CRUD operation
    with patch.object(crud_constitution, "get_constitution") as mock_get:
        mock_get.return_value = None
        
        # Make the request
        response = client.get(f"/api/v1/constitution/{TEST_ID}")
        
        # Assert the response
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "not found" in response.json()["detail"]
        
        # Verify the mock was called
        mock_get.assert_called_once_with(mock_db_session, constitution_id=TEST_ID)

def test_update_constitution(mock_db_session, test_constitution_model):
    """Test updating a constitution."""
    # Mock the CRUD operations
    with patch.object(crud_constitution, "get_constitution") as mock_get, \
         patch.object(crud_constitution, "update_constitution") as mock_update:
        mock_get.return_value = test_constitution_model
        mock_update.return_value = test_constitution_model
        
        # Create update data
        update_data = AIConstitutionUpdate(
            title="Updated Constitution",
            updated_by="updater"
        ).dict(exclude_unset=True)
        
        # Make the request
        response = client.put(f"/api/v1/constitution/{TEST_ID}", json=update_data)
        
        # Assert the response
        assert response.status_code == 200
        assert response.json()["id"] == TEST_ID
        assert response.json()["title"] == "Test Constitution"  # Mock returns original
        
        # Verify the mocks were called
        mock_get.assert_called_once_with(mock_db_session, constitution_id=TEST_ID)
        mock_update.assert_called_once_with(
            db=mock_db_session,
            db_constitution=test_constitution_model,
            constitution_update=update_data
        )

def test_delete_constitution(mock_db_session):
    """Test deleting a constitution."""
    # Mock the CRUD operation
    with patch.object(crud_constitution, "delete_constitution") as mock_delete:
        mock_delete.return_value = True
        
        # Make the request
        response = client.delete(f"/api/v1/constitution/{TEST_ID}")
        
        # Assert the response
        assert response.status_code == 204
        
        # Verify the mock was called
        mock_delete.assert_called_once_with(mock_db_session, constitution_id=TEST_ID)

def test_delete_constitution_not_found(mock_db_session):
    """Test deleting a constitution that doesn't exist."""
    # Mock the CRUD operation
    with patch.object(crud_constitution, "delete_constitution") as mock_delete:
        mock_delete.return_value = False
        
        # Make the request
        response = client.delete(f"/api/v1/constitution/{TEST_ID}")
        
        # Assert the response
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "not found" in response.json()["detail"]
        
        # Verify the mock was called
        mock_delete.assert_called_once_with(mock_db_session, constitution_id=TEST_ID)

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.schemas.pir import PolicySynthesisResponse, PIR
from datetime import datetime, timezone

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@patch('app.services.llm_service.LLMService.synthesize_policy')
async def test_synthesize_policy(mock_synthesize, db_session):
    """Test policy synthesis endpoint."""
    # Mock the LLM service response
    mock_response = PolicySynthesisResponse(
        policy=PIR(
            id="test-id",
            name="Test Policy",
            description="Test policy description",
            status="draft",
            version=1,
            trigger_conditions=[{"condition_type": "prompt_pattern", "parameters": {"patterns": ["test"]}}],
            governance_actions=[{"action_type": "block_execution", "parameters": {"message": "Test"}, "priority": 100}],
            tags=[],
            metadata_={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by="test",
            updated_by="test"
        ),
        explanation="Test explanation",
        confidence=0.95,
        warnings=[]
    )
    
    mock_synthesize.return_value = mock_response
    
    # Test request
    request_data = {
        "policy_intent": "Test policy intent",
        "context": {"test": "test"},
        "constraints": ["constraint1"],
        "examples": []
    }
    
    response = client.post("/api/v1/synthesize", json=request_data)
    assert response.status_code == 201
    assert response.json()["policy"]["name"] == "Test Policy"

def test_get_synthesis_examples():
    """Test the synthesis examples endpoint."""
    response = client.get("/api/v1/synthesize/examples")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

@patch('app.services.llm_service.LLMService.synthesize_policy')
async def test_synthesize_policy_validation_error(mock_synthesize):
    """Test policy synthesis with invalid input."""
    # Mock the LLM service to raise a validation error
    mock_synthesize.side_effect = ValueError("Invalid policy format")
    
    # Test with invalid request data
    request_data = {"invalid": "data"}
    response = client.post("/api/v1/synthesize", json=request_data)
    assert response.status_code == 422  # Validation error

@patch('app.services.llm_service.LLMService.synthesize_policy')
async def test_synthesize_policy_server_error(mock_synthesize):
    """Test policy synthesis with server error."""
    # Mock the LLM service to raise an exception
    mock_synthesize.side_effect = Exception("Server error")
    
    # Test request
    request_data = {
        "policy_intent": "Test policy intent",
        "context": {},
        "constraints": [],
        "examples": []
    }
    
    response = client.post("/api/v1/synthesize", json=request_data)
    assert response.status_code == 500  # Internal server error
    assert "Failed to synthesize policy" in response.json()["detail"]

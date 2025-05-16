import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.schemas.pir import PolicySynthesisRequest, PolicySynthesisResponse, PIR
from datetime import datetime, timezone

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@patch('app.api.v1.endpoints.synthesize.LLMService')
async def test_synthesize_policy(mock_llm_service, db_session):
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
    
    # Configure the mock
    mock_service_instance = MagicMock()
    mock_service_instance.synthesize_policy.return_value = mock_response
    mock_llm_service.return_value = mock_service_instance
    
    # Test request
    request_data = {
        "policy_intent": "Test policy intent",
        "context": {"test": "test"},
        "constraints": ["constraint1"],
        "examples": []
    }
    
    response = client.post("/api/v1/synthesize", json=request_data)
    
    # Assert the response
    assert response.status_code == 201
    assert response.json()["policy"]["name"] == "Test Policy"
    assert response.json()["explanation"] == "Test explanation"
    
    # Verify the LLM service was called with the correct arguments
    mock_service_instance.synthesize_policy.assert_called_once()
    args, _ = mock_service_instance.synthesize_policy.call_args
    assert isinstance(args[0], PolicySynthesisRequest)
    assert args[0].policy_intent == "Test policy intent"

@patch('app.api.v1.endpoints.synthesize.LLMService')
async def test_synthesize_policy_validation_error(mock_llm_service):
    """Test policy synthesis with invalid input."""
    # Test with invalid request data (missing required fields)
    request_data = {"invalid": "data"}
    response = client.post("/api/v1/synthesize", json=request_data)
    
    # Assert the response
    assert response.status_code == 422  # Validation error
    
    # Verify the LLM service was not called
    mock_llm_service.assert_not_called()

@patch('app.api.v1.endpoints.synthesize.LLMService')
async def test_synthesize_policy_service_error(mock_llm_service):
    """Test policy synthesis with service error."""
    # Configure the mock to raise an exception
    mock_service_instance = MagicMock()
    mock_service_instance.synthesize_policy.side_effect = Exception("Service error")
    mock_llm_service.return_value = mock_service_instance
    
    # Test request
    request_data = {
        "policy_intent": "Test policy intent",
        "context": {},
        "constraints": [],
        "examples": []
    }
    
    response = client.post("/api/v1/synthesize", json=request_data)
    
    # Assert the response
    assert response.status_code == 500
    assert "Failed to synthesize policy" in response.json()["detail"]

def test_get_synthesis_examples():
    """Test the synthesis examples endpoint."""
    response = client.get("/api/v1/synthesize/examples")
    
    # Assert the response
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    
    # Check the structure of the first example
    example = response.json()[0]
    assert "intent" in example
    assert "context" in example
    assert "constraints" in example

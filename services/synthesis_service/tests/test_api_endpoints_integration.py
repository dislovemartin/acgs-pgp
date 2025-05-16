import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
import json

from app.main import app
from app.schemas.pir import PolicySynthesisRequest, PolicySynthesisResponse, PIR, TriggerCondition, GovernanceAction

# Create test client
client = TestClient(app)

# Test data
TEST_POLICY_INTENT = "Test policy intent"
TEST_CONTEXT = {"domain": "test-domain", "regulations": ["GDPR"]}
TEST_CONSTRAINTS = ["constraint1", "constraint2"]
TEST_EXAMPLES = ["example1", "example2"]

# Fixtures

@pytest.fixture
def mock_policy_response():
    """Create a mock policy response."""
    return PolicySynthesisResponse(
        policy=PIR(
            id="test-id",
            name="Test Policy",
            description="Test policy description",
            status="draft",
            version=1,
            trigger_conditions=[
                TriggerCondition(
                    condition_type="prompt_pattern",
                    parameters={"patterns": ["test"]},
                    description="Test condition"
                )
            ],
            governance_actions=[
                GovernanceAction(
                    action_type="block_execution",
                    parameters={"message": "Test"},
                    priority=100,
                    description="Test action"
                )
            ],
            tags=["test"],
            metadata_={"test": "test"},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by="test",
            updated_by="test"
        ),
        explanation="Test explanation",
        confidence=0.95,
        warnings=[]
    )

# Tests

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "ACGS-PGP Synthesis Service",
        "version": "0.1.0"
    }

@patch('app.api.v1.endpoints.synthesize.LLMService')
async def test_synthesize_policy_endpoint(mock_llm_service, mock_policy_response):
    """Test the policy synthesis endpoint."""
    # Configure the mock LLM service
    mock_service_instance = AsyncMock()
    mock_service_instance.synthesize_policy.return_value = mock_policy_response
    mock_llm_service.return_value = mock_service_instance
    
    # Prepare the request payload
    request_data = {
        "policy_intent": TEST_POLICY_INTENT,
        "context": TEST_CONTEXT,
        "constraints": TEST_CONSTRAINTS,
        "examples": TEST_EXAMPLES
    }
    
    # Make the request
    response = client.post("/api/v1/synthesize", json=request_data)
    
    # Assert the response
    assert response.status_code == 201
    response_data = response.json()
    assert "policy" in response_data
    assert "explanation" in response_data
    assert "confidence" in response_data
    assert "warnings" in response_data
    
    # Verify the policy data
    policy_data = response_data["policy"]
    assert policy_data["name"] == "Test Policy"
    assert policy_data["description"] == "Test policy description"
    assert policy_data["status"] == "draft"
    assert len(policy_data["trigger_conditions"]) == 1
    assert len(policy_data["governance_actions"]) == 1
    
    # Verify the LLM service was called with the correct arguments
    mock_service_instance.synthesize_policy.assert_called_once()
    args, _ = mock_service_instance.synthesize_policy.call_args
    assert isinstance(args[0], PolicySynthesisRequest)
    assert args[0].policy_intent == TEST_POLICY_INTENT
    assert args[0].context == TEST_CONTEXT
    assert args[0].constraints == TEST_CONSTRAINTS
    assert args[0].examples == TEST_EXAMPLES

@patch('app.api.v1.endpoints.synthesize.LLMService')
async def test_synthesize_policy_validation_error(mock_llm_service):
    """Test validation error in the policy synthesis endpoint."""
    # Make a request with invalid data (missing required fields)
    response = client.post("/api/v1/synthesize", json={"invalid": "data"})
    
    # Assert the response
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()
    
    # Verify the LLM service was not called
    mock_llm_service.assert_not_called()

@patch('app.api.v1.endpoints.synthesize.LLMService')
async def test_synthesize_policy_service_error(mock_llm_service):
    """Test service error in the policy synthesis endpoint."""
    # Configure the mock LLM service to raise an exception
    mock_service_instance = AsyncMock()
    mock_service_instance.synthesize_policy.side_effect = Exception("Service error")
    mock_llm_service.return_value = mock_service_instance
    
    # Prepare the request payload
    request_data = {
        "policy_intent": TEST_POLICY_INTENT,
        "context": TEST_CONTEXT,
        "constraints": TEST_CONSTRAINTS,
        "examples": TEST_EXAMPLES
    }
    
    # Make the request
    response = client.post("/api/v1/synthesize", json=request_data)
    
    # Assert the response
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "Failed to synthesize policy" in response.json()["detail"]

def test_get_synthesis_examples():
    """Test the synthesis examples endpoint."""
    # Make the request
    response = client.get("/api/v1/synthesize/examples")
    
    # Assert the response
    assert response.status_code == 200
    examples = response.json()
    assert isinstance(examples, list)
    assert len(examples) > 0
    
    # Check the structure of each example
    for example in examples:
        assert "intent" in example
        assert "context" in example
        assert "constraints" in example
        assert "examples" in example

@patch('app.api.v1.endpoints.synthesize.LLMService')
async def test_synthesize_policy_rate_limiting(mock_llm_service, mock_policy_response):
    """Test rate limiting in the policy synthesis endpoint."""
    # Configure the mock LLM service
    mock_service_instance = AsyncMock()
    mock_service_instance.synthesize_policy.return_value = mock_policy_response
    mock_llm_service.return_value = mock_service_instance
    
    # Prepare the request payload
    request_data = {
        "policy_intent": TEST_POLICY_INTENT,
        "context": TEST_CONTEXT,
        "constraints": TEST_CONSTRAINTS,
        "examples": TEST_EXAMPLES
    }
    
    # Make multiple requests in quick succession
    # Note: This is a simplified test; in a real scenario, you'd use a proper rate limiting test
    for _ in range(3):
        response = client.post("/api/v1/synthesize", json=request_data)
        assert response.status_code == 201
    
    # Verify the LLM service was called the correct number of times
    assert mock_service_instance.synthesize_policy.call_count == 3

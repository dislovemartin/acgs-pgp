import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from app.services.llm_service import LLMService
from app.schemas.pir import PolicySynthesisRequest, PolicySynthesisResponse, PIR, TriggerCondition, GovernanceAction
from datetime import datetime, timezone

# Test data
TEST_API_KEY = "test-api-key"
TEST_MODEL = "gpt-4"
TEST_POLICY_INTENT = "Test policy intent"
TEST_CONTEXT = {"domain": "test-domain", "regulations": ["GDPR"]}
TEST_CONSTRAINTS = ["constraint1", "constraint2"]
TEST_EXAMPLES = ["example1", "example2"]

# Fixtures

@pytest.fixture
def llm_service():
    """Create an LLMService instance for testing."""
    return LLMService(api_key=TEST_API_KEY, model=TEST_MODEL)

@pytest.fixture
def mock_policy_response():
    """Create a mock policy response."""
    return {
        "name": "Test Policy",
        "description": "Test policy description",
        "status": "draft",
        "trigger_conditions": [
            {"condition_type": "prompt_pattern", "parameters": {"patterns": ["test"]}}
        ],
        "governance_actions": [
            {"action_type": "block_execution", "parameters": {"message": "Test"}, "priority": 100}
        ],
        "tags": ["test"],
        "metadata": {"test": "test"}
    }

# Tests

@pytest.mark.asyncio
async def test_synthesize_policy_success(llm_service, mock_policy_response):
    """Test successful policy synthesis."""
    # Mock the OpenAI API response
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = json.dumps(mock_policy_response)
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    # Patch the OpenAI client
    with patch('openai.AsyncOpenAI') as mock_openai:
        # Configure the mock client
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create a test request
        request = PolicySynthesisRequest(
            policy_intent=TEST_POLICY_INTENT,
            context=TEST_CONTEXT,
            constraints=TEST_CONSTRAINTS,
            examples=TEST_EXAMPLES
        )
        
        # Call the method under test
        result = await llm_service.synthesize_policy(request)
        
        # Assertions
        assert isinstance(result, PolicySynthesisResponse)
        assert result.policy.name == "Test Policy"
        assert result.policy.description == "Test policy description"
        assert result.policy.status == "draft"
        assert len(result.policy.trigger_conditions) == 1
        assert len(result.policy.governance_actions) == 1
        assert result.confidence > 0
        
        # Verify the OpenAI API was called with the correct parameters
        mock_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == TEST_MODEL
        assert "messages" in kwargs
        assert len(kwargs["messages"]) > 0
        assert "temperature" in kwargs

@pytest.mark.asyncio
async def test_synthesize_policy_invalid_json(llm_service):
    """Test handling of invalid JSON response from the LLM."""
    # Mock the OpenAI API response with invalid JSON
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "invalid json"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    # Patch the OpenAI client
    with patch('openai.AsyncOpenAI') as mock_openai:
        # Configure the mock client
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create a test request
        request = PolicySynthesisRequest(
            policy_intent=TEST_POLICY_INTENT,
            context=TEST_CONTEXT,
            constraints=TEST_CONSTRAINTS,
            examples=TEST_EXAMPLES
        )
        
        # Call the method and expect a ValueError
        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            await llm_service.synthesize_policy(request)

@pytest.mark.asyncio
async def test_synthesize_policy_api_error(llm_service):
    """Test handling of API errors from the LLM service."""
    # Patch the OpenAI client to raise an exception
    with patch('openai.AsyncOpenAI') as mock_openai:
        # Configure the mock client to raise an exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        
        # Create a test request
        request = PolicySynthesisRequest(
            policy_intent=TEST_POLICY_INTENT,
            context=TEST_CONTEXT,
            constraints=TEST_CONSTRAINTS,
            examples=TEST_EXAMPLES
        )
        
        # Call the method and expect the exception to be propagated
        with pytest.raises(Exception, match="API error"):
            await llm_service.synthesize_policy(request)

def test_generate_example_requests(llm_service):
    """Test generation of example policy synthesis requests."""
    # Call the method
    examples = llm_service.generate_example_requests()
    
    # Assertions
    assert isinstance(examples, list)
    assert len(examples) > 0
    
    # Check the structure of each example
    for example in examples:
        assert "intent" in example
        assert "context" in example
        assert "constraints" in example
        assert "examples" in example
        
        # Check that the context is a dictionary
        assert isinstance(example["context"], dict)
        
        # Check that constraints and examples are lists
        assert isinstance(example["constraints"], list)
        assert isinstance(example["examples"], list)

@pytest.mark.asyncio
async def test_synthesize_policy_with_invalid_response_structure(llm_service):
    """Test handling of invalid response structure from the LLM."""
    # Mock the OpenAI API response with invalid structure
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = json.dumps({"invalid": "response"})  # Missing required fields
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    # Patch the OpenAI client
    with patch('openai.AsyncOpenAI') as mock_openai:
        # Configure the mock client
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create a test request
        request = PolicySynthesisRequest(
            policy_intent=TEST_POLICY_INTENT,
            context=TEST_CONTEXT,
            constraints=TEST_CONSTRAINTS,
            examples=TEST_EXAMPLES
        )
        
        # Call the method and expect a validation error
        with pytest.raises(ValueError, match="Invalid policy format"):
            await llm_service.synthesize_policy(request)

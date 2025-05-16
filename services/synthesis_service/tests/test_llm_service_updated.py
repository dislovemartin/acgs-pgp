import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
import json
import sys
import os

# Add the parent directory to the path so we can import the common schemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from common.schemas.pir import (
    PIR, TriggerCondition, GovernanceAction,
    TriggerConditions, PromptPattern, ContextAttribute,
    ToolUsageRequest, ResponsePattern,
    Scope, PolicyStatus, PolicySeverity,
    TriggerConditionType, GovernanceActionType,
    ScopeModelInclusionType, ScopeUserRoleInclusionType,
    ScopeApplicationInclusionType, ScopeDataSensitivityInclusionType
)

from app.services.llm_service import LLMService
from app.schemas.pir import PolicySynthesisRequest, PolicySynthesisResponse

# Test data
TEST_TIMESTAMP = datetime.now(timezone.utc)
TEST_API_KEY = "test-api-key"
TEST_MODEL = "gpt-4"
TEST_POLICY_INTENT = "Create a policy to prevent PII disclosure"
TEST_CONTEXT = {"domain": "healthcare", "regulations": ["HIPAA", "GDPR"]}
TEST_CONSTRAINTS = ["Must block execution if PII is detected", "Must apply to all user roles"]

@pytest.fixture
def llm_service():
    """Create an LLMService instance for testing."""
    with patch('openai.OpenAI') as mock_client:
        service = LLMService()
        # Override the settings-based values with our test values
        service.client = AsyncMock()
        service.model = TEST_MODEL
        yield service

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response with a detailed P-IR."""
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "policy": {
                            "name": "PII Disclosure Prevention Policy",
                            "description": "This policy prevents the disclosure of personally identifiable information (PII) in AI responses.",
                            "status": "draft",
                            "constitutional_references": ["privacy.1", "security.3"],
                            "scope": {
                                "llm_models_inclusion": "all",
                                "llm_models_list": [],
                                "user_roles_inclusion": "all",
                                "user_roles_list": [],
                                "applications_inclusion": "all",
                                "applications_list": [],
                                "data_sensitivity_inclusion": "minimum",
                                "data_sensitivity_levels": ["public", "internal", "confidential", "restricted"]
                            },
                            "trigger_conditions": {
                                "prompt_patterns": [
                                    {
                                        "pattern": "social security",
                                        "is_regex": False,
                                        "case_sensitive": False,
                                        "description": "Match SSN mentions"
                                    },
                                    {
                                        "pattern": "\\d{3}-\\d{2}-\\d{4}",
                                        "is_regex": True,
                                        "case_sensitive": False,
                                        "description": "Match SSN format"
                                    }
                                ],
                                "context_attributes": [],
                                "tool_usage_requests": [],
                                "response_patterns": [],
                                "custom_conditions": [],
                                "condition_logic": "ANY"
                            },
                            "governance_actions": [
                                {
                                    "action_type": "block_execution",
                                    "parameters": {
                                        "message": "This prompt contains potentially sensitive PII and cannot be processed."
                                    },
                                    "priority": 100,
                                    "description": "Block execution when PII is detected"
                                }
                            ],
                            "severity": "high",
                            "priority": 80,
                            "tags": ["security", "compliance", "pii"],
                            "version": 1,
                            "created_by": "system",
                            "updated_by": "system",
                            "metadata": {
                                "compliance_standards": ["HIPAA", "GDPR"],
                                "custom_metadata": {
                                    "domain": "healthcare"
                                }
                            }
                        },
                        "explanation": "This policy is designed to prevent the disclosure of PII, specifically Social Security Numbers, in AI interactions. It scans for common patterns of SSNs in prompts and blocks execution if detected.",
                        "confidence": 0.95,
                        "warnings": ["This policy only detects explicit mentions of SSNs and may not catch all forms of PII."]
                    })
                }
            }
        ]
    }

@pytest.fixture
def mock_openai_response_legacy():
    """Create a mock OpenAI response with a legacy P-IR format."""
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "policy": {
                            "name": "PII Disclosure Prevention Policy",
                            "description": "This policy prevents the disclosure of personally identifiable information (PII) in AI responses.",
                            "status": "draft",
                            "trigger_conditions": [
                                {
                                    "condition_type": "prompt_pattern",
                                    "parameters": {
                                        "patterns": ["social security", "\\d{3}-\\d{2}-\\d{4}"]
                                    },
                                    "description": "Match SSN mentions or format"
                                }
                            ],
                            "governance_actions": [
                                {
                                    "action_type": "block_execution",
                                    "parameters": {
                                        "message": "This prompt contains potentially sensitive PII and cannot be processed."
                                    },
                                    "priority": 100,
                                    "description": "Block execution when PII is detected"
                                }
                            ],
                            "tags": ["security", "compliance", "pii"],
                            "version": 1,
                            "created_by": "system",
                            "updated_by": "system",
                            "metadata": {
                                "compliance_standards": ["HIPAA", "GDPR"]
                            }
                        },
                        "explanation": "This policy is designed to prevent the disclosure of PII, specifically Social Security Numbers, in AI interactions.",
                        "confidence": 0.95,
                        "warnings": ["This policy only detects explicit mentions of SSNs."]
                    })
                }
            }
        ]
    }

@pytest.mark.asyncio
async def test_synthesize_policy_with_detailed_schema(llm_service, mock_openai_response):
    """Test policy synthesis with the detailed P-IR schema."""
    # Create a proper mock response object that matches the OpenAI client's response structure
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    content = mock_openai_response['choices'][0]['message']['content']
    mock_response.choices[0].message.content = content

    # Mock the chat.completions.create method
    llm_service.client.chat.completions.create.return_value = mock_response

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent=TEST_POLICY_INTENT,
        context=TEST_CONTEXT,
        constraints=TEST_CONSTRAINTS
    )

    # Call the method
    response = await llm_service.synthesize_policy(request)

    # Assertions
    assert response.policy.name == "PII Disclosure Prevention Policy"
    expected_desc = ("This policy prevents the disclosure of personally "
                     "identifiable information (PII) in AI responses.")
    assert response.policy.description == expected_desc
    assert response.policy.status == PolicyStatus.DRAFT
    assert response.policy.constitutional_references == ["privacy.1", "security.3"]

    # Check scope
    assert response.policy.scope.llm_models_inclusion == ScopeModelInclusionType.ALL
    assert (response.policy.scope.data_sensitivity_inclusion ==
            ScopeDataSensitivityInclusionType.MINIMUM)
    expected_levels = ["public", "internal", "confidential", "restricted"]
    assert response.policy.scope.data_sensitivity_levels == expected_levels

    # Check trigger conditions
    assert isinstance(response.policy.trigger_conditions, TriggerConditions)
    assert len(response.policy.trigger_conditions.prompt_patterns) == 2
    assert response.policy.trigger_conditions.prompt_patterns[0].pattern == "social security"
    assert response.policy.trigger_conditions.condition_logic == "ANY"

    # Check governance actions
    assert len(response.policy.governance_actions) == 1
    assert response.policy.governance_actions[0].action_type == GovernanceActionType.BLOCK_EXECUTION
    assert response.policy.governance_actions[0].priority == 100

    # Check other fields
    assert response.policy.severity == PolicySeverity.HIGH
    assert response.policy.priority == 80
    assert response.policy.tags == ["security", "compliance", "pii"]

    # Check explanation with a partial match to avoid long line
    explanation = response.explanation
    assert "prevent the disclosure of PII" in explanation
    assert "Social Security Numbers" in explanation
    assert "scans for common patterns" in explanation

    assert response.confidence == 0.95
    assert len(response.warnings) == 1

# pylint: disable=redefined-outer-name
@pytest.mark.asyncio
async def test_synthesize_policy_with_legacy_schema(llm_service, mock_openai_response_legacy):
    """Test policy synthesis with the legacy P-IR schema."""
    # Create a proper mock response object that matches the OpenAI client's response structure
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    content = mock_openai_response_legacy['choices'][0]['message']['content']
    mock_response.choices[0].message.content = content

    # Mock the chat.completions.create method
    llm_service.client.chat.completions.create.return_value = mock_response

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent=TEST_POLICY_INTENT,
        context=TEST_CONTEXT,
        constraints=TEST_CONSTRAINTS
    )

    # Call the method
    response = await llm_service.synthesize_policy(request)

    # Assertions
    assert response.policy.name == "PII Disclosure Prevention Policy"
    expected_desc = ("This policy prevents the disclosure of personally "
                     "identifiable information (PII) in AI responses.")
    assert response.policy.description == expected_desc
    assert response.policy.status == PolicyStatus.DRAFT

    # Check trigger conditions (legacy format)
    assert isinstance(response.policy.trigger_conditions, list)
    assert len(response.policy.trigger_conditions) == 1
    condition_type = response.policy.trigger_conditions[0].condition_type
    assert condition_type == TriggerConditionType.PROMPT_PATTERN

    expected_patterns = {"patterns": ["social security", "\\d{3}-\\d{2}-\\d{4}"]}
    assert response.policy.trigger_conditions[0].parameters == expected_patterns

    # Check governance actions
    assert len(response.policy.governance_actions) == 1
    assert response.policy.governance_actions[0].action_type == GovernanceActionType.BLOCK_EXECUTION
    assert response.policy.governance_actions[0].priority == 100

    # Check other fields
    assert response.policy.tags == ["security", "compliance", "pii"]

    # Check explanation with a partial match to avoid long line
    explanation = response.explanation
    assert "prevent the disclosure of PII" in explanation
    assert "Social Security Numbers" in explanation

    assert response.confidence == 0.95
    assert len(response.warnings) == 1

# pylint: disable=redefined-outer-name
@pytest.mark.asyncio
async def test_system_prompt_contains_detailed_schema(llm_service):
    """Test that the system prompt contains instructions for the detailed schema."""
    # Using a protected method is acceptable in tests
    # pylint: disable=protected-access
    system_prompt = llm_service._create_system_prompt()

    # Check for detailed schema elements in the system prompt
    assert "constitutional_references" in system_prompt
    assert "scope" in system_prompt
    assert "llm_models_inclusion" in system_prompt
    assert "data_sensitivity_inclusion" in system_prompt
    assert "trigger_conditions" in system_prompt
    assert "prompt_patterns" in system_prompt
    assert "context_attributes" in system_prompt
    assert "tool_usage_requests" in system_prompt
    assert "response_patterns" in system_prompt
    assert "condition_logic" in system_prompt
    assert "severity" in system_prompt
    assert "priority" in system_prompt

# pylint: disable=redefined-outer-name
@pytest.mark.asyncio
async def test_synthesize_policy_with_minimal_data(llm_service):
    """Test policy synthesis with minimal data in the response."""
    # Create a minimal mock response
    minimal_response = {
        "policy": {
            "name": "Minimal Policy",
            "description": "A minimal policy with only required fields",
            "trigger_conditions": {},
            "governance_actions": [
                {
                    "action_type": "log_action",
                    "parameters": {"message": "Minimal action"}
                }
            ]
        },
        "explanation": "Minimal explanation",
        "warnings": []
    }

    # Create a proper mock response object
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps(minimal_response)

    # Mock the chat.completions.create method
    llm_service.client.chat.completions.create.return_value = mock_response

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent="Create a minimal policy"
    )

    # Call the method
    response = await llm_service.synthesize_policy(request)

    # Assertions for minimal data
    assert response.policy.name == "Minimal Policy"
    assert response.policy.description == "A minimal policy with only required fields"
    assert response.policy.status == PolicyStatus.DRAFT  # Default value
    assert isinstance(response.policy.trigger_conditions, TriggerConditions)
    assert len(response.policy.governance_actions) == 1
    assert response.policy.governance_actions[0].action_type == GovernanceActionType.LOG_ACTION
    assert response.policy.severity == PolicySeverity.MEDIUM  # Default value
    assert response.policy.priority == 50  # Default value
    assert response.explanation == "Minimal explanation"
    assert len(response.warnings) == 0

@pytest.mark.asyncio
async def test_synthesize_policy_handles_invalid_json(llm_service):
    """Test that the service handles invalid JSON responses gracefully."""
    # Create a mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "{invalid json"

    # Mock the chat.completions.create method
    llm_service.client.chat.completions.create.return_value = mock_response

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent="Create a policy"
    )

    # Call the method and expect an exception
    with pytest.raises(ValueError) as excinfo:
        await llm_service.synthesize_policy(request)

    # Check that the error message mentions invalid JSON
    assert "Invalid JSON" in str(excinfo.value)

@pytest.mark.asyncio
async def test_synthesize_policy_handles_empty_response(llm_service):
    """Test that the service handles empty responses gracefully."""
    # Create a mock response with empty content
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = ""

    # Mock the chat.completions.create method
    llm_service.client.chat.completions.create.return_value = mock_response

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent="Create a policy"
    )

    # Call the method and expect an exception
    with pytest.raises(ValueError) as excinfo:
        await llm_service.synthesize_policy(request)

    # Check that the error message mentions empty response
    assert "Empty response" in str(excinfo.value)

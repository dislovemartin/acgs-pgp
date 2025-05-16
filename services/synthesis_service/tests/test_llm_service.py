import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm_service import LLMService
from app.schemas.pir import PolicySynthesisRequest, PIR, PolicySynthesisResponse
from datetime import datetime, timezone
import markdown

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response with Markdown content."""
    return {
        "choices": [
            {
                "message": {
                    "content": """# AI Constitution for Test Application

## 1. Core Identity and Purpose

This AI system is designed to assist users with general tasks while maintaining strict ethical boundaries.

## 2. Critical Prohibitions

- MUST NOT provide legal advice
- MUST NOT generate harmful content

## 3. Data Handling Protocols

All user data must be treated as confidential.

## 4. Tool Usage Guidelines

When using tools, the system must verify permissions before execution.
""",
                    "role": "assistant"
                }
            }
        ]
    }

@pytest.fixture
def llm_service():
    """Create an instance of LLMService with a mock client."""
    with patch('openai.OpenAI') as mock_client:
        service = LLMService()
        service.client = AsyncMock()
        service.model = "gpt-4"
        service.temperature = 0.7
        yield service

@pytest.mark.asyncio
async def test_synthesize_policy_success(llm_service, mock_openai_response):
    """Test successful policy synthesis with Markdown output."""
    # Mock the chat.completions.create method
    llm_service.client.chat.completions.create.return_value = MagicMock(**mock_openai_response)

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent="Test policy intent",
        context={
            "application_name": "Test App",
            "application_domain": "Testing",
            "target_users_description": "Test users",
            "supported_languages": ["English"],
            "available_tools": ["test_tool"],
            "compliance_mandates": ["Test Compliance"],
            "ethical_guidelines": ["Be ethical"],
            "output_style_requirements": ["Be clear"],
            "data_sensitivity_levels": ["Standard"],
            "runtime_placeholders": ["{{test}}"]
        },
        constraints=["MUST NOT provide legal advice"],
        examples=[]
    )

    # Call the method under test
    response = await llm_service.synthesize_policy(request)

    # Assert the response
    assert isinstance(response, PolicySynthesisResponse)
    assert "Test App" in response.policy.name
    assert "Testing" in response.policy.description
    assert len(response.policy.trigger_conditions.prompt_patterns) > 0
    assert len(response.policy.governance_actions) > 0
    assert response.policy.status == "draft"
    assert "synthesized" in response.policy.tags

@pytest.mark.asyncio
async def test_synthesize_policy_empty_response(llm_service):
    """Test handling of empty response from LLM."""
    # Mock the chat.completions.create method to return empty content
    llm_service.client.chat.completions.create.return_value = MagicMock(**{
        "choices": [
            {
                "message": {
                    "content": '',
                    "role": "assistant"
                }
            }
        ]
    })

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent="Test policy intent",
        context={
            "application_name": "Test App",
            "application_domain": "Testing"
        },
        constraints=[],
        examples=[]
    )

    # Call the method under test and expect a ValueError
    with pytest.raises(ValueError, match="Empty Markdown response"):
        await llm_service.synthesize_policy(request)

@pytest.mark.asyncio
async def test_synthesize_policy_api_error(llm_service):
    """Test handling of API errors from OpenAI."""
    # Mock the chat.completions.create method to raise an exception
    llm_service.client.chat.completions.create.side_effect = Exception("API error")

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent="Test policy intent",
        context={
            "application_name": "Test App",
            "application_domain": "Testing"
        },
        constraints=[],
        examples=[]
    )

    # Call the method under test and expect an exception
    with pytest.raises(Exception, match="API error"):
        await llm_service.synthesize_policy(request)

def test_create_system_prompt():
    """Test the _create_system_prompt method."""
    service = LLMService()
    system_prompt = service._create_system_prompt()

    # Assert the system prompt contains key elements from META_SYSTEM_PROMPT_V1_0
    assert "<META_AI_IDENTITY_AND_OBJECTIVE>" in system_prompt
    assert "Promethean Governance Synthesizer (PGS-AI)" in system_prompt
    assert "<CORE_COMPILATION_PRINCIPLES_FOR_AI_CONSTITUTIONS>" in system_prompt

    # Test the _create_user_prompt method
    request = PolicySynthesisRequest(
        policy_intent="Test policy intent",
        context={
            "application_name": "Test App",
            "application_domain": "Testing"
        },
        constraints=["No harmful content"],
        examples=[]
    )

    user_prompt = service._create_user_prompt(request)

    # Assert the user prompt contains expected elements
    assert "applicationName: Test App" in user_prompt
    assert "applicationDomain: Testing" in user_prompt
    assert "coreMissionAndTasks: Test policy intent" in user_prompt

def test_parse_markdown_constitution_to_pir():
    """Test the _parse_markdown_constitution_to_pir method."""
    service = LLMService()

    # Create a test markdown constitution
    markdown_text = """# AI Constitution for Test App

## 1. Core Identity and Purpose

This AI system is designed to assist users with general tasks.

## 2. Critical Prohibitions

- MUST NOT provide legal advice
- MUST NOT generate harmful content

## 3. Data Handling Protocols

All user data must be treated as confidential.
"""

    # Create a test request
    request = PolicySynthesisRequest(
        policy_intent="Test policy intent",
        context={
            "application_name": "Test App",
            "application_domain": "Testing",
            "compliance_mandates": ["GDPR", "HIPAA"]
        },
        constraints=["MUST NOT provide legal advice"],
        examples=[]
    )

    # Parse the markdown to PIR
    pir = service._parse_markdown_constitution_to_pir(markdown_text, request)

    # Assert the PIR contains expected elements
    assert "Test App" in pir.name
    assert "Testing" in pir.description
    assert len(pir.trigger_conditions.prompt_patterns) > 0
    assert len(pir.governance_actions) > 0
    assert pir.status == PolicyStatus.DRAFT
    assert "testing" in pir.tags
    assert "synthesized" in pir.tags
    assert pir.metadata.compliance_standards == ["GDPR", "HIPAA"]
    assert pir.metadata.synthesis_details.synthesized_by == "PGS-AI (via LLMService)"

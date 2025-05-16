import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from app.schemas.pir import (
    TriggerCondition,
    GovernanceAction,
    PIR,
    PolicySynthesisRequest,
    PolicySynthesisResponse
)

# Test data
TEST_TIMESTAMP = datetime.now(timezone.utc)

def test_trigger_condition_validation():
    """Test validation of TriggerCondition model."""
    # Test valid trigger condition
    condition = TriggerCondition(
        condition_type="prompt_pattern",
        parameters={"patterns": ["test"]},
        description="Test condition"
    )

    assert condition.condition_type == "prompt_pattern"
    assert condition.parameters == {"patterns": ["test"]}
    assert condition.description == "Test condition"

    # Test with missing required field
    with pytest.raises(ValidationError):
        TriggerCondition(
            condition_type="prompt_pattern",
            # Missing parameters
            description="Test condition"
        )

    # Test with invalid condition type
    with pytest.raises(ValidationError):
        TriggerCondition(
            condition_type="invalid_type",
            parameters={"test": "value"},
            description="Test condition"
        )

def test_governance_action_validation():
    """Test validation of GovernanceAction model."""
    # Test valid governance action
    action = GovernanceAction(
        action_type="block_execution",
        parameters={"message": "Test"},
        priority=100,
        description="Test action"
    )

    assert action.action_type == "block_execution"
    assert action.parameters == {"message": "Test"}
    assert action.priority == 100
    assert action.description == "Test action"

    # Test with invalid action type
    with pytest.raises(ValidationError):
        GovernanceAction(
            action_type="invalid_action",
            parameters={"test": "value"},
            priority=100,
            description="Test action"
        )

def test_pir_model_validation():
    """Test validation of PIR model."""
    # Test valid PIR
    pir = PIR(
        policy_id="test-id",
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
        metadata={"test": "test"},
        created_at=TEST_TIMESTAMP,
        updated_at=TEST_TIMESTAMP,
        created_by="test",
        updated_by="test"
    )

    assert pir.policy_id == "test-id"
    assert pir.name == "Test Policy"
    assert pir.status == "draft"
    assert pir.version == 1
    assert len(pir.trigger_conditions) == 1
    assert len(pir.governance_actions) == 1
    assert pir.tags == ["test"]
    assert isinstance(pir.metadata, dict)

    # Test with invalid status
    with pytest.raises(ValidationError):
        PIR(
            policy_id="test-id",
            name="Test Policy",
            description="Test policy description",
            status="invalid_status",
            version=1,
            trigger_conditions=[],
            governance_actions=[],
            created_at=TEST_TIMESTAMP,
            updated_at=TEST_TIMESTAMP,
            created_by="test",
            updated_by="test"
        )

def test_policy_synthesis_request_validation():
    """Test validation of PolicySynthesisRequest model."""
    # Test valid request
    request = PolicySynthesisRequest(
        policy_intent="Test policy intent",
        context={"domain": "test"},
        constraints=["constraint1", "constraint2"],
        examples=[{"intent": "example1", "policy": {}}, {"intent": "example2", "policy": {}}]
    )

    assert request.policy_intent == "Test policy intent"
    assert request.context == {"domain": "test"}
    assert request.constraints == ["constraint1", "constraint2"]
    assert len(request.examples) == 2

    # Test with missing required field
    with pytest.raises(ValidationError):
        PolicySynthesisRequest(
            # Missing policy_intent
            context={"domain": "test"},
            constraints=[],
            examples=[]
        )

def test_policy_synthesis_response_validation():
    """Test validation of PolicySynthesisResponse model."""
    # Test valid response
    response = PolicySynthesisResponse(
        policy=PIR(
            policy_id="test-id",
            name="Test Policy",
            description="Test policy description",
            status="draft",
            version=1,
            trigger_conditions=[],
            governance_actions=[],
            created_at=TEST_TIMESTAMP,
            updated_at=TEST_TIMESTAMP,
            created_by="test",
            updated_by="test"
        ),
        explanation="Test explanation",
        confidence=0.95,
        warnings=["warning1", "warning2"]
    )

    assert response.policy.name == "Test Policy"
    assert response.explanation == "Test explanation"
    assert response.confidence == 0.95
    assert response.warnings == ["warning1", "warning2"]

    # Test with confidence out of range
    with pytest.raises(ValidationError):
        PolicySynthesisResponse(
            policy=PIR(
                policy_id="test-id",
                name="Test Policy",
                description="Test policy description",
                status="draft",
                version=1,
                trigger_conditions=[],
                governance_actions=[],
                created_at=TEST_TIMESTAMP,
                updated_at=TEST_TIMESTAMP,
                created_by="test",
                updated_by="test"
            ),
            explanation="Test explanation",
            confidence=1.5,  # Invalid confidence
            warnings=[]
        )

def test_pir_model_serialization():
    """Test serialization and deserialization of PIR model."""
    # Create a PIR instance
    pir = PIR(
        policy_id="test-id",
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
        metadata={"test": "test"},
        created_at=TEST_TIMESTAMP,
        updated_at=TEST_TIMESTAMP,
        created_by="test",
        updated_by="test"
    )

    # Convert to dict
    pir_dict = pir.dict()

    # Convert back to PIR
    pir_from_dict = PIR(**pir_dict)

    # Assert the round-trip was successful
    assert pir_from_dict.policy_id == pir.policy_id
    assert pir_from_dict.name == pir.name
    assert pir_from_dict.status == pir.status
    assert len(pir_from_dict.trigger_conditions) == len(pir.trigger_conditions)
    assert len(pir_from_dict.governance_actions) == len(pir.governance_actions)
    assert pir_from_dict.tags == pir.tags

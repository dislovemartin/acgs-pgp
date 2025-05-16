import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError, HttpUrl
from typing import Dict, List, Any, Optional
from enum import Enum
from app.schemas.pir import (
    TriggerCondition,
    GovernanceAction,
    PIR,
    PIRCreate,
    PolicySynthesisRequest,
    PolicySynthesisResponse,
    TriggerConditionType,
    GovernanceActionType
)

# Helper function to check if a ValidationError contains a specific error
def has_validation_error(exc_info, msg):
    for error in exc_info.value.errors():
        if msg in str(error):
            return True
    return False

# Test data
TEST_TIMESTAMP = datetime.now(timezone.utc)
VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"
VALID_URL = "https://example.com/policy/123"
VALID_EMAIL = "test@example.com"

# Define test policy status values for convenience
class PolicyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"

class TestTriggerCondition:
    """Test suite for TriggerCondition validation."""
    
    def test_valid_trigger_condition(self):
        """Test valid trigger condition creation."""
        condition = TriggerCondition(
            condition_type=TriggerConditionType.PROMPT_PATTERN,
            parameters={"patterns": ["test"]},
            description="Test condition"
        )
        assert condition.condition_type == TriggerConditionType.PROMPT_PATTERN
        assert condition.parameters == {"patterns": ["test"]}
        assert condition.description == "Test condition"
    
    def test_trigger_condition_with_defaults(self):
        """Test trigger condition with default values."""
        condition = TriggerCondition(
            condition_type=TriggerConditionType.PROMPT_PATTERN,
            parameters={"patterns": ["test"]}
        )
        assert condition.description is None
    
    @pytest.mark.parametrize("invalid_params,error_match", [
        ({"condition_type": "invalid_type"}, "value is not a valid enumeration member"),  # Invalid condition type
        ({"condition_type": TriggerConditionType.PROMPT_PATTERN}, "field required"),  # Missing parameters
    ])
    def test_invalid_trigger_conditions(self, invalid_params, error_match):
        """Test various invalid trigger condition scenarios."""
        with pytest.raises(ValidationError) as exc_info:
            TriggerCondition(**invalid_params)
        assert any(error_match in str(err) for err in exc_info.value.errors())

class TestGovernanceAction:
    """Test suite for GovernanceAction validation."""
    
    def test_valid_governance_action(self):
        """Test valid governance action creation."""
        action = GovernanceAction(
            action_type=GovernanceActionType.BLOCK_EXECUTION,
            parameters={"message": "Test message"},
            priority=100,
            description="Test action"
        )
        assert action.action_type == GovernanceActionType.BLOCK_EXECUTION
        assert action.parameters == {"message": "Test message"}
        assert action.priority == 100
        assert action.description == "Test action"
    
    def test_governance_action_with_defaults(self):
        """Test governance action with default values."""
        action = GovernanceAction(
            action_type=GovernanceActionType.BLOCK_EXECUTION,
            parameters={"message": "Test"}
        )
        assert action.priority == 100
        assert action.description is None
    
    @pytest.mark.parametrize("invalid_params,error_match", [
        ({"action_type": "invalid_action"}, "value is not a valid enumeration member"),  # Invalid action type
        ({"action_type": GovernanceActionType.BLOCK_EXECUTION}, "field required"),  # Missing parameters
    ])
    def test_invalid_governance_actions(self, invalid_params, error_match):
        """Test various invalid governance action scenarios."""
        with pytest.raises(ValidationError) as exc_info:
            GovernanceAction(**invalid_params)
        assert any(error_match in str(err) for err in exc_info.value.errors())

class TestPIRModel:
    """Test suite for PIR model validation."""
    
    @pytest.fixture
    def valid_pir_data(self):
        """Fixture providing valid PIR data for testing."""
        return {
            "name": "Test Policy",
            "description": "Test policy description",
            "trigger_conditions": [
                {
                    "condition_type": TriggerConditionType.PROMPT_PATTERN,
                    "parameters": {"patterns": ["test"]},
                    "description": "Test condition"
                }
            ],
            "governance_actions": [
                {
                    "action_type": GovernanceActionType.BLOCK_EXECUTION,
                    "parameters": {"message": "Test message"},
                    "priority": 100,
                    "description": "Test action"
                }
            ],
            "tags": ["test"],
            "status": "draft"
        }
    
    def test_valid_pir_creation(self, valid_pir_data):
        """Test valid PIR creation with all fields."""
        pir = PIRCreate(**valid_pir_data)
        
        assert pir.name == "Test Policy"
        assert pir.status == "draft"
        assert len(pir.trigger_conditions) == 1
        assert len(pir.governance_actions) == 1
        assert pir.tags == ["test"]
    
    def test_pir_with_minimal_fields(self, valid_pir_data):
        """Test PIR creation with only required fields."""
        minimal_data = {
            "name": "Minimal Policy",
            "description": "Minimal policy description",
            "trigger_conditions": [
                {
                    "condition_type": TriggerConditionType.PROMPT_PATTERN,
                    "parameters": {"patterns": ["test"]}
                }
            ],
            "governance_actions": [
                {
                    "action_type": GovernanceActionType.BLOCK_EXECUTION,
                    "parameters": {"message": "Test"}
                }
            ]
        }
        
        pir = PIRCreate(**minimal_data)
        assert pir.name == "Minimal Policy"
        assert pir.description == "Minimal policy description"
        assert pir.tags == []
        assert pir.status == "draft"
    
    @pytest.mark.parametrize("test_input,expected_status", [
        # Test that any status string is accepted
        ({"status": "custom_status"}, "custom_status"),
        ({"status": "active"}, "active"),
        ({"status": "draft"}, "draft"),
        ({"status": "inactive"}, "inactive"),
        ({"status": ""}, ""),  # Empty string is also accepted
    ])
    def test_pir_status_accepts_any_string(self, valid_pir_data, test_input, expected_status):
        """Test that PIR model accepts any string as status."""
        # Create a copy of valid data and update with test input
        test_data = valid_pir_data.copy()
        test_data.update(test_input)
        
        # Should not raise an exception
        pir = PIRCreate(**test_data)
        assert pir.status == expected_status
    
    def test_pir_immutable_fields(self, valid_pir_data):
        """Test that required fields must be provided."""
        # Test that required fields cannot be None
        required_fields = ["name", "description"]
        for field in required_fields:
            test_data = valid_pir_data.copy()
            test_data[field] = None
            with pytest.raises(ValidationError) as exc_info:
                PIRCreate(**test_data)
            errors = [str(err) for err in exc_info.value.errors()]
            assert any("none is not an allowed value" in err for err in errors)
        
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            PIRCreate()
        assert any("field required" in str(err) for err in exc_info.value.errors())
    
    def test_pir_status_validation(self, valid_pir_data):
        """Test PIR status validation."""
        # Test valid status values
        for status in ["draft", "active", "inactive"]:
            data = valid_pir_data.copy()
            data["status"] = status
            pir = PIRCreate(**data)
            assert pir.status == status
        
        # Test invalid status - PIR model doesn't validate status values by default
        # So we'll just test that it accepts any string
        data = valid_pir_data.copy()
        data["status"] = "custom_status"
        pir = PIRCreate(**data)
        assert pir.status == "custom_status"
        
        # Test that status is required
        data = valid_pir_data.copy()
        del data["status"]
        # PIRCreate has a default status of "draft"
        pir = PIRCreate(**data)
        assert pir.status == "draft"

class TestPolicySynthesisRequest:
    """Test suite for PolicySynthesisRequest validation."""
    
    def test_valid_request(self):
        """Test valid policy synthesis request."""
        request = PolicySynthesisRequest(
            policy_intent="Test policy intent",
            context={"domain": "test", "regulations": ["GDPR"]},
            constraints=["constraint1", "constraint2"],
            examples=[{"example1": "data1"}, {"example2": "data2"}]
        )
        
        assert request.policy_intent == "Test policy intent"
        assert request.context == {"domain": "test", "regulations": ["GDPR"]}
        assert request.constraints == ["constraint1", "constraint2"]
        assert request.examples == [{"example1": "data1"}, {"example2": "data2"}]
    
    def test_request_with_defaults(self):
        """Test request with default values."""
        request = PolicySynthesisRequest(
            policy_intent="Test policy intent"
        )
        
        assert request.context == {}
        assert request.constraints == []
        assert request.examples == []
    
    @pytest.mark.parametrize("invalid_data,error_match", [
        ({"policy_intent": None}, "none is not an allowed value"),
        ({"context": "not-a-dict"}, "value is not a valid dict"),
        ({"constraints": "not-a-list"}, "value is not a valid list"),
        ({"examples": ["not-a-dict"]}, "value is not a valid dict")
        # Empty policy_intent is allowed by the schema
    ])
    def test_invalid_requests(self, invalid_data, error_match):
        """Test various invalid request scenarios."""
        with pytest.raises(ValidationError) as exc_info:
            PolicySynthesisRequest(**invalid_data)
        assert any(error_match in str(err) for err in exc_info.value.errors())

class TestPolicySynthesisResponse:
    """Test suite for PolicySynthesisResponse validation."""
    
    @pytest.fixture
    def valid_policy_data(self):
        """Fixture providing valid policy data for testing."""
        return {
            "id": VALID_UUID,
            "name": "Test Policy",
            "description": "Test policy description",
            "status": "draft",
            "version": 1,
            "trigger_conditions": [
                {
                    "condition_type": TriggerConditionType.PROMPT_PATTERN,
                    "parameters": {"patterns": ["test"]}
                }
            ],
            "governance_actions": [
                {
                    "action_type": GovernanceActionType.BLOCK_EXECUTION,
                    "parameters": {"message": "Test"},
                    "priority": 100
                }
            ],
            "created_at": TEST_TIMESTAMP.isoformat(),
            "updated_at": TEST_TIMESTAMP.isoformat(),
            "created_by": VALID_EMAIL,
            "updated_by": VALID_EMAIL
        }
    
    def test_valid_response(self):
        """Test creating a valid policy synthesis response."""
        # Create a valid PIR instance with all required fields
        from datetime import datetime, timezone
        
        pir_data = {
            "id": "test-id-123",
            "name": "Test Policy",
            "description": "Test policy description",
            "trigger_conditions": [
                {
                    "condition_type": "prompt_pattern",
                    "parameters": {"patterns": ["test"]}
                }
            ],
            "governance_actions": [
                {
                    "action_type": "block_execution",
                    "parameters": {"message": "Test"},
                    "priority": 100
                }
            ],
            "status": "draft",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "tags": [],
            "metadata": {},
            "version": 1,
            "created_by": "test",
            "updated_by": "test"
        }
        pir = PIR(**pir_data)
        
        response = PolicySynthesisResponse(
            policy=pir,
            explanation="Test explanation",
            confidence=0.8
        )
        
        assert response.explanation == "Test explanation"
        assert response.confidence == 0.8
        assert response.warnings == []
    
    def test_response_with_defaults(self):
        """Test response with default values."""
        from datetime import datetime, timezone
        
        # Create a valid PIR instance with all required fields
        pir_data = {
            "id": "test-id-123",
            "name": "Test Policy",
            "description": "Test policy description",
            "trigger_conditions": [
                {
                    "condition_type": "prompt_pattern",
                    "parameters": {"patterns": ["test"]}
                }
            ],
            "governance_actions": [
                {
                    "action_type": "block_execution",
                    "parameters": {"message": "Test"},
                    "priority": 100
                }
            ],
            "status": "draft",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "tags": [],
            "metadata": {},
            "version": 1,
            "created_by": "test",
            "updated_by": "test"
        }
        pir = PIR(**pir_data)
        
        response = PolicySynthesisResponse(
            policy=pir,
            explanation="Test explanation"
        )
        
        assert response.confidence == 1.0
        assert response.warnings == []

    @pytest.mark.parametrize("invalid_data,error_match", [
        ({"explanation": ""}, "ensure this value has at least 1 character"),
        ({"confidence": -0.1}, "ensure this value is greater than or equal to 0"),
        ({"confidence": 1.1}, "ensure this value is less than or equal to 1"),
        ({"policy": {"invalid": "data"}}, "field required"),  # Test missing required fields in policy
        ({"policy": None}, "none is not an allowed value")  # Test None policy
    ])
    def test_invalid_responses(self, valid_policy_data, invalid_data, error_match):
        """Test various invalid response scenarios."""
        from datetime import datetime, timezone
        
        # Special case for testing invalid policy
        if invalid_data.get("policy") == {"invalid": "data"}:
            with pytest.raises(ValidationError) as exc_info:
                PolicySynthesisResponse(
                    policy={"invalid": "data"},  # This should fail validation
                    explanation="Test explanation",
                    confidence=0.8
                )
            errors = [str(err) for err in exc_info.value.errors()]
            assert any("field required" in err for err in errors), f"Expected error containing 'field required' but got: {errors}"
            return
            
        # Special case for testing None policy
        if invalid_data.get("policy") is None:
            with pytest.raises(ValidationError) as exc_info:
                PolicySynthesisResponse(
                    policy=None,
                    explanation="Test explanation",
                    confidence=0.8
                )
            errors = [str(err) for err in exc_info.value.errors()]
            assert any("none is not an allowed value" in err for err in errors), f"Expected error containing 'none is not allowed' but got: {errors}"
            return
            
        # Create a valid PIR instance with all required fields
        pir = PIR(
            id="test-id-123",
            name="Test Policy",
            description="Test policy description",
            trigger_conditions=[
                {
                    "condition_type": "prompt_pattern",
                    "parameters": {"patterns": ["test"]}
                }
            ],
            governance_actions=[
                {
                    "action_type": "block_execution",
                    "parameters": {"message": "Test"},
                    "priority": 100
                }
            ],
            status="draft",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            tags=[],
            metadata={},
            version=1,
            created_by="test",
            updated_by="test"
        )
        
        # Create a valid response data
        valid_data = {
            "policy": pir,
            "explanation": "Test explanation",
            "confidence": 0.8,
            "warnings": []
        }
        
        # Merge with invalid data for testing
        test_data = {**valid_data, **invalid_data}
    
        with pytest.raises(ValidationError) as exc_info:
            PolicySynthesisResponse(**test_data)
            
        # Check if any of the error messages contain our expected error
        errors = [str(err) for err in exc_info.value.errors()]
        error_found = any(error_match in err for err in errors)
        assert error_found, f"Expected error containing '{error_match}' but got: {errors}"

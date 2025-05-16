import pytest
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

from app.engine.policy_evaluator import PolicyEvaluator, PolicyEvaluation

# Test data
TEST_TIMESTAMP = datetime.now(timezone.utc)

@pytest.fixture
def policy_with_legacy_conditions():
    """Create a test policy with legacy trigger conditions."""
    return PIR(
        policy_id="test-legacy-id",
        name="Test Legacy Policy",
        description="Test policy with legacy conditions",
        status=PolicyStatus.ACTIVE,
        version=1,
        trigger_conditions=[
            TriggerCondition(
                condition_type=TriggerConditionType.PROMPT_PATTERN,
                parameters={"patterns": ["test pattern", "sensitive"]},
                description="Test pattern condition"
            ),
            TriggerCondition(
                condition_type=TriggerConditionType.TOOL_USAGE,
                parameters={"tool_names": ["sensitive_tool"]},
                description="Sensitive tool usage condition"
            )
        ],
        governance_actions=[
            GovernanceAction(
                action_type=GovernanceActionType.BLOCK_EXECUTION,
                parameters={"message": "This action is blocked due to policy violation."},
                priority=100,
                description="Block execution action"
            )
        ],
        scope=Scope(),
        constitutional_references=[],
        severity=PolicySeverity.HIGH,
        priority=80,
        tags=["test", "security"],
        created_at=TEST_TIMESTAMP,
        updated_at=TEST_TIMESTAMP,
        created_by="test-user",
        updated_by="test-user",
        metadata={}
    )

@pytest.fixture
def policy_with_structured_conditions():
    """Create a test policy with structured trigger conditions."""
    return PIR(
        policy_id="test-structured-id",
        name="Test Structured Policy",
        description="Test policy with structured conditions",
        status=PolicyStatus.ACTIVE,
        version=1,
        trigger_conditions=TriggerConditions(
            prompt_patterns=[
                PromptPattern(
                    pattern="test pattern",
                    is_regex=False,
                    case_sensitive=False,
                    description="Test pattern"
                ),
                PromptPattern(
                    pattern="sensitive",
                    is_regex=False,
                    case_sensitive=False,
                    description="Sensitive pattern"
                )
            ],
            context_attributes=[
                ContextAttribute(
                    attribute_name="user_role",
                    attribute_value="admin",
                    match_type="exact",
                    description="Admin user"
                )
            ],
            tool_usage_requests=[
                ToolUsageRequest(
                    tool_name="sensitive_tool",
                    parameter_constraints={"access_level": "high"},
                    description="Sensitive tool usage"
                )
            ],
            response_patterns=[
                ResponsePattern(
                    pattern="confidential",
                    is_regex=False,
                    case_sensitive=False,
                    description="Confidential information in response"
                )
            ],
            condition_logic="ANY"
        ),
        governance_actions=[
            GovernanceAction(
                action_type=GovernanceActionType.BLOCK_EXECUTION,
                parameters={"message": "This action is blocked due to policy violation."},
                priority=100,
                description="Block execution action"
            )
        ],
        scope=Scope(
            llm_models_inclusion=ScopeModelInclusionType.INCLUDE,
            llm_models_list=["gpt-4", "claude-3"],
            user_roles_inclusion=ScopeUserRoleInclusionType.ALL,
            applications_inclusion=ScopeApplicationInclusionType.ALL,
            data_sensitivity_inclusion=ScopeDataSensitivityInclusionType.MINIMUM,
            data_sensitivity_levels=["public", "internal", "confidential"]
        ),
        constitutional_references=["privacy.1", "security.3"],
        severity=PolicySeverity.HIGH,
        priority=80,
        tags=["test", "security"],
        created_at=TEST_TIMESTAMP,
        updated_at=TEST_TIMESTAMP,
        created_by="test-user",
        updated_by="test-user",
        metadata={}
    )

@pytest.fixture
def policy_evaluator():
    """Create a policy evaluator instance."""
    return PolicyEvaluator()

class TestPolicyEvaluator:
    """Test suite for PolicyEvaluator."""
    
    def test_evaluate_legacy_policy_match(self, policy_evaluator, policy_with_legacy_conditions):
        """Test evaluating a policy with legacy conditions that match."""
        prompt = "This is a test pattern that should trigger the policy."
        metadata = {}
        
        result = policy_evaluator.evaluate_policies([policy_with_legacy_conditions], prompt, metadata)
        
        assert len(result) == 1
        assert result[0].policy.policy_id == "test-legacy-id"
        assert len(result[0].applied_actions) == 1
        assert result[0].applied_actions[0][0].action_type == GovernanceActionType.BLOCK_EXECUTION
    
    def test_evaluate_legacy_policy_no_match(self, policy_evaluator, policy_with_legacy_conditions):
        """Test evaluating a policy with legacy conditions that don't match."""
        prompt = "This prompt should not trigger the policy."
        metadata = {}
        
        result = policy_evaluator.evaluate_policies([policy_with_legacy_conditions], prompt, metadata)
        
        assert len(result) == 0
    
    def test_evaluate_structured_policy_prompt_match(self, policy_evaluator, policy_with_structured_conditions):
        """Test evaluating a policy with structured conditions that match on prompt pattern."""
        prompt = "This is a test pattern that should trigger the policy."
        metadata = {
            "model_name": "gpt-4",
            "user_role": "user",
            "data_sensitivity": "confidential"
        }
        
        result = policy_evaluator.evaluate_policies([policy_with_structured_conditions], prompt, metadata)
        
        assert len(result) == 1
        assert result[0].policy.policy_id == "test-structured-id"
        assert len(result[0].applied_actions) == 1
        assert result[0].applied_actions[0][0].action_type == GovernanceActionType.BLOCK_EXECUTION
    
    def test_evaluate_structured_policy_context_match(self, policy_evaluator, policy_with_structured_conditions):
        """Test evaluating a policy with structured conditions that match on context attribute."""
        prompt = "This prompt doesn't contain any trigger words."
        metadata = {
            "model_name": "gpt-4",
            "user_role": "admin",
            "data_sensitivity": "confidential"
        }
        
        result = policy_evaluator.evaluate_policies([policy_with_structured_conditions], prompt, metadata)
        
        assert len(result) == 1
        assert result[0].policy.policy_id == "test-structured-id"
    
    def test_evaluate_structured_policy_tool_match(self, policy_evaluator, policy_with_structured_conditions):
        """Test evaluating a policy with structured conditions that match on tool usage."""
        prompt = "This prompt doesn't contain any trigger words."
        metadata = {
            "model_name": "gpt-4",
            "user_role": "user",
            "data_sensitivity": "confidential",
            "tools_used": ["sensitive_tool"],
            "tool_parameters": {
                "sensitive_tool": {
                    "access_level": "high"
                }
            }
        }
        
        result = policy_evaluator.evaluate_policies([policy_with_structured_conditions], prompt, metadata)
        
        assert len(result) == 1
        assert result[0].policy.policy_id == "test-structured-id"
    
    def test_evaluate_structured_policy_response_match(self, policy_evaluator, policy_with_structured_conditions):
        """Test evaluating a policy with structured conditions that match on response pattern."""
        prompt = "This prompt doesn't contain any trigger words."
        metadata = {
            "model_name": "gpt-4",
            "user_role": "user",
            "data_sensitivity": "confidential",
            "response_text": "This response contains confidential information."
        }
        
        result = policy_evaluator.evaluate_policies([policy_with_structured_conditions], prompt, metadata)
        
        assert len(result) == 1
        assert result[0].policy.policy_id == "test-structured-id"
    
    def test_evaluate_structured_policy_no_match(self, policy_evaluator, policy_with_structured_conditions):
        """Test evaluating a policy with structured conditions that don't match."""
        prompt = "This prompt doesn't contain any trigger words."
        metadata = {
            "model_name": "gpt-4",
            "user_role": "user",
            "data_sensitivity": "public"
        }
        
        result = policy_evaluator.evaluate_policies([policy_with_structured_conditions], prompt, metadata)
        
        assert len(result) == 0
    
    def test_evaluate_structured_policy_out_of_scope(self, policy_evaluator, policy_with_structured_conditions):
        """Test evaluating a policy that's out of scope."""
        prompt = "This is a test pattern that should trigger the policy."
        metadata = {
            "model_name": "gpt-3.5-turbo",  # Not in the included models list
            "user_role": "user",
            "data_sensitivity": "confidential"
        }
        
        # Modify the policy to exclude gpt-3.5-turbo
        policy = policy_with_structured_conditions.copy()
        policy.scope.llm_models_inclusion = ScopeModelInclusionType.INCLUDE
        policy.scope.llm_models_list = ["gpt-4", "claude-3"]
        
        result = policy_evaluator.evaluate_policies([policy], prompt, metadata)
        
        assert len(result) == 0
    
    def test_evaluate_inactive_policy(self, policy_evaluator, policy_with_structured_conditions):
        """Test evaluating an inactive policy."""
        prompt = "This is a test pattern that should trigger the policy."
        metadata = {}
        
        # Modify the policy to be inactive
        policy = policy_with_structured_conditions.copy()
        policy.status = PolicyStatus.DRAFT
        
        result = policy_evaluator.evaluate_policies([policy], prompt, metadata)
        
        assert len(result) == 0
    
    def test_apply_governance_actions(self, policy_evaluator, policy_with_structured_conditions):
        """Test applying governance actions."""
        prompt = "This is a test pattern that should trigger the policy."
        metadata = {
            "model_name": "gpt-4",
            "user_role": "user",
            "data_sensitivity": "confidential"
        }
        
        result = policy_evaluator.evaluate_policies([policy_with_structured_conditions], prompt, metadata)
        
        assert len(result) == 1
        
        # Apply the governance actions
        modified_prompt, actions = policy_evaluator.apply_governance_actions(result, prompt)
        
        # The action is BLOCK_EXECUTION, so the prompt should not be modified
        assert modified_prompt == prompt
        assert len(actions) == 1
        assert actions[0]["action_type"] == GovernanceActionType.BLOCK_EXECUTION
        assert "message" in actions[0]["parameters"]

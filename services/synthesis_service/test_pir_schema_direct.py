#!/usr/bin/env python3
"""
Direct test for the PIR schema integration.
This test doesn't rely on the FastAPI app or other dependencies.
"""
import sys
import os
import json
from datetime import datetime, timezone
from pydantic import ValidationError

# Add the parent directory to the path so we can import the common schemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import the common PIR schema
from common.schemas.pir import (
    PIR, GovernanceAction, PolicyStatus, PolicySeverity, Scope,
    TriggerConditions, PromptPattern, ContextAttribute, ToolUsageRequest
)

def test_create_pir_with_common_schema():
    """Test creating a PIR using the common schema."""
    # Create a simple PIR
    try:
        # Create a Scope object
        scope = Scope(
            llm_models_list=["gpt-4", "claude-3"],
            llm_models_inclusion="include",
            user_roles_list=["admin", "user"],
            user_roles_inclusion="include",
            applications_list=["app1", "app2"],
            applications_inclusion="include",
            data_sensitivity_levels=["public", "internal", "confidential"],
            data_sensitivity_inclusion="minimum"
        )

        # Create TriggerConditions
        trigger_conditions = TriggerConditions(
            prompt_patterns=[
                PromptPattern(
                    pattern=r"\b\d{3}-\d{2}-\d{4}\b",
                    is_regex=True,
                    case_sensitive=False,
                    description="SSN format XXX-XX-XXXX"
                )
            ],
            context_attributes=[
                ContextAttribute(
                    attribute_name="user.role",
                    attribute_value="admin",
                    match_type="exact",
                    description="User is an admin"
                )
            ],
            tool_usage_requests=[
                ToolUsageRequest(
                    tool_name="email_sender",
                    parameter_constraints={
                        "to": "@example.com"
                    },
                    description="Email is being sent to example.com"
                )
            ],
            condition_logic="ALL"
        )

        # Create GovernanceActions
        governance_actions = [
            GovernanceAction(
                action_type="block_execution",
                parameters={
                    "message": "This action is not allowed"
                },
                description="Block the action"
            ),
            GovernanceAction(
                action_type="log_action",
                parameters={
                    "level": "warning",
                    "message": "Attempted to perform a restricted action"
                },
                description="Log the event"
            )
        ]

        # Create the PIR
        pir = PIR(
            policy_id="test-policy-id",
            name="Test Policy",
            description="Test policy description",
            status=PolicyStatus.DRAFT,
            constitutional_references=["PRIV-001", "SEC-002"],
            scope=scope,
            trigger_conditions=trigger_conditions,
            governance_actions=governance_actions,
            severity=PolicySeverity.HIGH,
            priority=100,
            tags=["test", "policy"],
            version=1,
            created_by="test-author",
            updated_by="test-author",
            metadata={
                "author": "test-author",
                "created_timestamp": datetime.now(timezone.utc).isoformat(),
                "last_updated_timestamp": datetime.now(timezone.utc).isoformat(),
                "custom_metadata": {
                    "test-key": "test-value"
                }
            }
        )

        # Validate the PIR
        pir_dict = pir.dict()
        print("PIR created successfully!")
        print(f"PIR ID: {pir.policy_id}")
        print(f"Description: {pir.description}")
        print(f"Status: {pir.status}")
        print(f"Severity: {pir.severity}")
        print(f"Priority: {pir.priority}")
        print(f"Trigger Conditions: {json.dumps(pir_dict['trigger_conditions'], indent=2)}")
        print(f"Governance Actions: {json.dumps(pir_dict['governance_actions'], indent=2)}")

        return True
    except ValidationError as e:
        print(f"Validation error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Run the test
    success = test_create_pir_with_common_schema()
    if success:
        print("\nTest passed!")
    else:
        print("\nTest failed!")
        sys.exit(1)

#!/usr/bin/env python3
"""
Script to generate test policies for formal verification.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Base directory for test data
TEST_DATA_DIR = Path(__file__).parent.parent / "tests" / "test_data"
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_policy(
    name: str,
    description: str,
    trigger_conditions: Dict[str, Any],
    governance_actions: List[Dict[str, Any]],
    temporal_logic: Dict[str, Any],
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate a policy dictionary with the given parameters."""
    policy_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    base_policy = {
        "policy_id": policy_id,
        "version": 1,
        "name": name,
        "description": description,
        "status": "DRAFT",
        "constitutional_references": ["constitution:data_retention"],
        "scope": {
            "resource_types": ["database"],
            "actions": ["read", "write", "delete"]
        },
        "trigger_conditions": trigger_conditions,
        "governance_actions": governance_actions,
        "severity": "HIGH",
        "priority": 50,
        "created_at": now,
        "updated_at": now,
        "created_by": "test_script",
        "updated_by": "test_script",
        "tags": ["test", "formal_verification"],
        "temporal_logic_annotations": temporal_logic,
        "metadata": metadata or {}
    }
    
    return base_policy

def generate_test_policies() -> List[Dict[str, Any]]:
    """Generate a list of test policies with different configurations."""
    policies = []
    
    # Policy 1: Simple data retention policy
    policies.append(generate_policy(
        name="Data Retention Policy - 30 Days",
        description="Automatically delete records older than 30 days",
        trigger_conditions={
            "allOf": [
                {"field": "record_age_days", "operator": ">=", "value": 30}
            ]
        },
        governance_actions=[
            {"action": "delete_record", "parameters": {"reason": "Retention policy enforcement"}}
        ],
        temporal_logic={
            "ltl_formula": "G(record_age_days >= 30 -> F(deleted = true))",
            "description": "Globally, if a record is older than 30 days, it will eventually be deleted"
        },
        metadata={
            "test_case": "simple_retention",
            "expected_verification_result": "SATISFIABLE"
        }
    ))
    
    # Policy 2: Access control with time restrictions
    policies.append(generate_policy(
        name="Time-based Access Control",
        description="Restrict access to sensitive data during non-business hours",
        trigger_conditions={
            "allOf": [
                {"field": "resource.sensitivity", "operator": "==", "value": "high"},
                {"anyOf": [
                    {"field": "time.hour", "operator": "<", "value": 9},
                    {"field": "time.hour", "operator": ">=", "value": 17}
                ]}
            ]
        },
        governance_actions=[
            {"action": "deny_access", "parameters": {"reason": "Access restricted outside business hours"}}
        ],
        temporal_logic={
            "ltl_formula": "G((time_hour < 9 | time_hour >= 17) & resource_sensitivity = 'high' -> X(access_granted = false))",
            "description": "Globally, if it's outside business hours (9-17) and the resource is highly sensitive, access is denied in the next state"
        },
        metadata={
            "test_case": "time_based_access",
            "expected_verification_result": "SATISFIABLE"
        }
    ))
    
    # Policy 3: Rate limiting policy
    policies.append(generate_policy(
        name="API Rate Limiting",
        description="Limit API calls to 1000 per hour per client",
        trigger_conditions={
            "allOf": [
                {"field": "api_calls_last_hour", "operator": ">", "value": 1000}
            ]
        },
        governance_actions=[
            {"action": "throttle_client", "parameters": {"duration_minutes": 60, "reason": "Rate limit exceeded"}}
        ],
        temporal_logic={
            "ltl_formula": "G(api_calls > 1000 -> X(throttled = true)) & G(throttled = true -> F(throttled = false))",
            "description": "If API calls exceed 1000, the client is throttled in the next state, and will eventually be unthrottled"
        },
        metadata={
            "test_case": "rate_limiting",
            "expected_verification_result": "SATISFIABLE"
        }
    ))
    
    return policies

def save_policies(policies: List[Dict[str, Any]]) -> None:
    """Save generated policies to JSON files."""
    for i, policy in enumerate(policies, 1):
        test_case = policy.get("metadata", {}).get("test_case", f"policy_{i}")
        filename = TEST_DATA_DIR / f"{test_case}.json"
        
        with open(filename, 'w') as f:
            json.dump(policy, f, indent=2)
        print(f"Generated {filename}")

def main():
    """Generate and save test policies."""
    print("Generating test policies...")
    policies = generate_test_policies()
    save_policies(policies)
    print(f"Generated {len(policies)} test policies in {TEST_DATA_DIR}")

if __name__ == "__main__":
    main()

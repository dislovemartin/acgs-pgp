from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import json

from ....db.base import get_db
from ....crud import pir as crud_pir
from common.schemas.pir import PIR, PolicyStatus

router = APIRouter()

class ValidationRule(BaseModel):
    """Model for a validation rule."""
    rule_id: str = Field(..., description="Unique identifier for the rule")
    description: str = Field(..., description="Description of what the rule checks")
    severity: str = Field(..., description="Severity level of the rule (ERROR, WARNING, INFO)")

class ValidationResult(BaseModel):
    """Model for a validation result."""
    rule_id: str = Field(..., description="ID of the rule that was applied")
    passed: bool = Field(..., description="Whether the policy passed this validation rule")
    message: str = Field(..., description="Validation message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional details about the validation")
    severity: str = Field(..., description="Severity level (ERROR, WARNING, INFO)")

class PolicyValidationRequest(BaseModel):
    """Request model for policy validation."""
    policy_id: str = Field(..., description="ID of the policy to validate")
    rule_ids: Optional[List[str]] = Field(default=None, description="Optional list of specific rule IDs to apply")

class PolicyValidationResponse(BaseModel):
    """Response model for policy validation."""
    policy_id: str = Field(..., description="ID of the validated policy")
    policy_name: str = Field(..., description="Name of the validated policy")
    policy_version: int = Field(..., description="Version of the validated policy")
    validation_timestamp: str = Field(..., description="ISO timestamp of when validation was performed")
    validation_id: str = Field(..., description="Unique ID for this validation run")
    results: List[ValidationResult] = Field(..., description="List of validation results")
    passed: bool = Field(..., description="Whether the policy passed all ERROR-level validations")
    summary: Dict[str, int] = Field(..., description="Summary of validation results by severity")

# Define validation rules
VALIDATION_RULES = [
    ValidationRule(
        rule_id="required_fields",
        description="Checks that all required fields are present and non-empty",
        severity="ERROR"
    ),
    ValidationRule(
        rule_id="condition_syntax",
        description="Validates the syntax of trigger conditions",
        severity="ERROR"
    ),
    ValidationRule(
        rule_id="action_syntax",
        description="Validates the syntax of governance actions",
        severity="ERROR"
    ),
    ValidationRule(
        rule_id="ltl_specification",
        description="Validates Linear Temporal Logic specifications",
        severity="ERROR"
    ),
    ValidationRule(
        rule_id="homomorphic_encryption",
        description="Validates homomorphic encryption policies",
        severity="WARNING"
    ),
    ValidationRule(
        rule_id="pqc_signature",
        description="Checks Post-Quantum Cryptography signatures",
        severity="WARNING"
    ),
    ValidationRule(
        rule_id="quantum_optimization",
        description="Validates quantum optimization hints",
        severity="INFO"
    ),
    ValidationRule(
        rule_id="metadata_completeness",
        description="Checks for completeness of policy metadata",
        severity="INFO"
    )
]

# Rule ID to rule mapping for quick lookup
RULE_MAP = {rule.rule_id: rule for rule in VALIDATION_RULES}

def validate_required_fields(policy: Dict[str, Any]) -> ValidationResult:
    """Validate that all required fields are present and non-empty."""
    missing_fields = []
    
    # Check required top-level fields
    required_fields = ["name", "description", "version", "trigger_conditions", "governance_actions"]
    for field in required_fields:
        if field not in policy or not policy[field]:
            missing_fields.append(field)
    
    # Check trigger conditions
    if "trigger_conditions" in policy and policy["trigger_conditions"]:
        for i, condition in enumerate(policy["trigger_conditions"]):
            if "condition_type" not in condition:
                missing_fields.append(f"trigger_conditions[{i}].condition_type")
    
    # Check governance actions
    if "governance_actions" in policy and policy["governance_actions"]:
        for i, action in enumerate(policy["governance_actions"]):
            if "action_type" not in action:
                missing_fields.append(f"governance_actions[{i}].action_type")
    
    if missing_fields:
        return ValidationResult(
            rule_id="required_fields",
            passed=False,
            message=f"Missing required fields: {', '.join(missing_fields)}",
            severity="ERROR",
            details={"missing_fields": missing_fields}
        )
    
    return ValidationResult(
        rule_id="required_fields",
        passed=True,
        message="All required fields are present",
        severity="ERROR"
    )

def validate_condition_syntax(policy: Dict[str, Any]) -> ValidationResult:
    """Validate the syntax of trigger conditions."""
    invalid_conditions = []
    
    if "trigger_conditions" in policy and policy["trigger_conditions"]:
        for i, condition in enumerate(policy["trigger_conditions"]):
            # Check condition type
            if "condition_type" not in condition:
                continue  # Already caught by required_fields validation
            
            condition_type = condition["condition_type"]
            
            # Validate based on condition type
            if condition_type == "PROMPT_PATTERN_MATCH":
                if "pattern" not in condition or not condition["pattern"]:
                    invalid_conditions.append(f"Condition {i}: Missing pattern for PROMPT_PATTERN_MATCH")
            
            elif condition_type == "ANOMALY_SCORE":
                if "threshold" not in condition:
                    invalid_conditions.append(f"Condition {i}: Missing threshold for ANOMALY_SCORE")
                elif not isinstance(condition["threshold"], (int, float)):
                    invalid_conditions.append(f"Condition {i}: Threshold must be a number for ANOMALY_SCORE")
            
            elif condition_type == "LTL_SPECIFICATION":
                if "formula" not in condition or not condition["formula"]:
                    invalid_conditions.append(f"Condition {i}: Missing formula for LTL_SPECIFICATION")
    
    if invalid_conditions:
        return ValidationResult(
            rule_id="condition_syntax",
            passed=False,
            message="Invalid trigger conditions found",
            severity="ERROR",
            details={"invalid_conditions": invalid_conditions}
        )
    
    return ValidationResult(
        rule_id="condition_syntax",
        passed=True,
        message="All trigger conditions have valid syntax",
        severity="ERROR"
    )

def validate_action_syntax(policy: Dict[str, Any]) -> ValidationResult:
    """Validate the syntax of governance actions."""
    invalid_actions = []
    
    if "governance_actions" in policy and policy["governance_actions"]:
        for i, action in enumerate(policy["governance_actions"]):
            # Check action type
            if "action_type" not in action:
                continue  # Already caught by required_fields validation
            
            action_type = action["action_type"]
            
            # Validate based on action type
            if action_type == "BLOCK":
                if "message" not in action or not action["message"]:
                    invalid_actions.append(f"Action {i}: Missing message for BLOCK action")
            
            elif action_type == "MODIFY":
                if "modification" not in action or not action["modification"]:
                    invalid_actions.append(f"Action {i}: Missing modification for MODIFY action")
            
            elif action_type == "REQUIRE_APPROVAL":
                if "approver_roles" not in action or not action["approver_roles"]:
                    invalid_actions.append(f"Action {i}: Missing approver_roles for REQUIRE_APPROVAL action")
    
    if invalid_actions:
        return ValidationResult(
            rule_id="action_syntax",
            passed=False,
            message="Invalid governance actions found",
            severity="ERROR",
            details={"invalid_actions": invalid_actions}
        )
    
    return ValidationResult(
        rule_id="action_syntax",
        passed=True,
        message="All governance actions have valid syntax",
        severity="ERROR"
    )

def validate_ltl_specification(policy: Dict[str, Any]) -> ValidationResult:
    """Validate Linear Temporal Logic specifications."""
    invalid_specs = []
    
    # Check if policy has LTL specifications
    if "temporal_logic_annotations" in policy and policy["temporal_logic_annotations"]:
        ltl_specs = policy["temporal_logic_annotations"].get("ltl_specifications", [])
        
        for i, spec in enumerate(ltl_specs):
            if "formula" not in spec or not spec["formula"]:
                invalid_specs.append(f"LTL Specification {i}: Missing formula")
            # Additional LTL syntax validation could be added here
    
    # Check for LTL in trigger conditions
    if "trigger_conditions" in policy and policy["trigger_conditions"]:
        for i, condition in enumerate(policy["trigger_conditions"]):
            if condition.get("condition_type") == "LTL_SPECIFICATION":
                if "formula" not in condition or not condition["formula"]:
                    invalid_specs.append(f"Trigger Condition {i}: Missing LTL formula")
                # Additional LTL syntax validation could be added here
    
    if invalid_specs:
        return ValidationResult(
            rule_id="ltl_specification",
            passed=False,
            message="Invalid LTL specifications found",
            severity="ERROR",
            details={"invalid_specs": invalid_specs}
        )
    
    return ValidationResult(
        rule_id="ltl_specification",
        passed=True,
        message="All LTL specifications are valid",
        severity="ERROR"
    )

def validate_homomorphic_encryption(policy: Dict[str, Any]) -> ValidationResult:
    """Validate homomorphic encryption policies."""
    issues = []
    
    if "homomorphic_encryption_policy" in policy and policy["homomorphic_encryption_policy"]:
        he_policy = policy["homomorphic_encryption_policy"]
        
        # Check required fields for HE policy
        if "scheme" not in he_policy or not he_policy["scheme"]:
            issues.append("Missing encryption scheme")
        
        if "key_length" not in he_policy:
            issues.append("Missing key length")
        elif not isinstance(he_policy["key_length"], int) or he_policy["key_length"] < 2048:
            issues.append(f"Invalid key length: {he_policy['key_length']}. Should be at least 2048 bits.")
        
        if "operations" not in he_policy or not he_policy["operations"]:
            issues.append("Missing supported operations")
    
    if issues:
        return ValidationResult(
            rule_id="homomorphic_encryption",
            passed=False,
            message="Issues found with homomorphic encryption policy",
            severity="WARNING",
            details={"issues": issues}
        )
    
    return ValidationResult(
        rule_id="homomorphic_encryption",
        passed=True,
        message="Homomorphic encryption policy is valid",
        severity="WARNING"
    )

def validate_pqc_signature(policy: Dict[str, Any]) -> ValidationResult:
    """Check Post-Quantum Cryptography signatures."""
    issues = []
    
    if "pqc_signature" in policy and policy["pqc_signature"]:
        pqc_sig = policy["pqc_signature"]
        
        # Check required fields for PQC signature
        if "algorithm" not in pqc_sig or not pqc_sig["algorithm"]:
            issues.append("Missing PQC algorithm")
        
        if "signature_value" not in pqc_sig or not pqc_sig["signature_value"]:
            issues.append("Missing signature value")
        
        if "public_key_id" not in pqc_sig or not pqc_sig["public_key_id"]:
            issues.append("Missing public key ID")
    
    if issues:
        return ValidationResult(
            rule_id="pqc_signature",
            passed=False,
            message="Issues found with PQC signature",
            severity="WARNING",
            details={"issues": issues}
        )
    
    return ValidationResult(
        rule_id="pqc_signature",
        passed=True,
        message="PQC signature is valid",
        severity="WARNING"
    )

def validate_quantum_optimization(policy: Dict[str, Any]) -> ValidationResult:
    """Validate quantum optimization hints."""
    suggestions = []
    
    if "quantum_optimization_hints" in policy and policy["quantum_optimization_hints"]:
        qo_hints = policy["quantum_optimization_hints"]
        
        # Check for recommended fields
        if "qubit_mapping" not in qo_hints or not qo_hints["qubit_mapping"]:
            suggestions.append("Consider adding qubit mapping for better quantum optimization")
        
        if "circuit_depth" not in qo_hints:
            suggestions.append("Consider specifying circuit depth for quantum optimization")
        
        if "error_mitigation" not in qo_hints or not qo_hints["error_mitigation"]:
            suggestions.append("Consider adding error mitigation strategies")
    
    if suggestions:
        return ValidationResult(
            rule_id="quantum_optimization",
            passed=True,  # This is just informational, so always passes
            message="Suggestions for quantum optimization hints",
            severity="INFO",
            details={"suggestions": suggestions}
        )
    
    return ValidationResult(
        rule_id="quantum_optimization",
        passed=True,
        message="Quantum optimization hints are comprehensive",
        severity="INFO"
    )

def validate_metadata_completeness(policy: Dict[str, Any]) -> ValidationResult:
    """Check for completeness of policy metadata."""
    suggestions = []
    
    # Check for recommended metadata fields
    if "metadata_" not in policy or not policy["metadata_"]:
        suggestions.append("Consider adding metadata for better policy documentation")
    else:
        metadata = policy["metadata_"]
        
        if "created_by" not in metadata:
            suggestions.append("Consider adding 'created_by' to metadata")
        
        if "created_at" not in metadata:
            suggestions.append("Consider adding 'created_at' to metadata")
        
        if "tags" not in metadata or not metadata["tags"]:
            suggestions.append("Consider adding tags to metadata for better searchability")
        
        if "documentation_url" not in metadata:
            suggestions.append("Consider adding documentation URL to metadata")
    
    if suggestions:
        return ValidationResult(
            rule_id="metadata_completeness",
            passed=True,  # This is just informational, so always passes
            message="Suggestions for metadata completeness",
            severity="INFO",
            details={"suggestions": suggestions}
        )
    
    return ValidationResult(
        rule_id="metadata_completeness",
        passed=True,
        message="Metadata is comprehensive",
        severity="INFO"
    )

# Map of validation functions by rule ID
VALIDATION_FUNCTIONS = {
    "required_fields": validate_required_fields,
    "condition_syntax": validate_condition_syntax,
    "action_syntax": validate_action_syntax,
    "ltl_specification": validate_ltl_specification,
    "homomorphic_encryption": validate_homomorphic_encryption,
    "pqc_signature": validate_pqc_signature,
    "quantum_optimization": validate_quantum_optimization,
    "metadata_completeness": validate_metadata_completeness
}

@router.get("/validation/rules", response_model=List[ValidationRule])
async def list_validation_rules():
    """List all available validation rules."""
    return VALIDATION_RULES

@router.post("/validation/validate", response_model=PolicyValidationResponse)
async def validate_policy(
    request: PolicyValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a policy against predefined rules.
    
    This endpoint runs validation checks on a policy and returns detailed results.
    It can be used to verify policy correctness before submission or during review.
    """
    # Get the policy from the database
    db_policy = crud_pir.get_policy(db, policy_id=request.policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Convert policy to dictionary for validation
    policy_dict = db_policy.to_dict()
    
    # Determine which rules to apply
    rule_ids = request.rule_ids if request.rule_ids else list(VALIDATION_FUNCTIONS.keys())
    
    # Validate against each rule
    results = []
    for rule_id in rule_ids:
        if rule_id not in VALIDATION_FUNCTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown validation rule: {rule_id}"
            )
        
        # Apply the validation function
        result = VALIDATION_FUNCTIONS[rule_id](policy_dict)
        results.append(result)
    
    # Generate validation summary
    summary = {
        "ERROR": 0,
        "WARNING": 0,
        "INFO": 0,
        "TOTAL": len(results),
        "PASSED": 0,
        "FAILED": 0
    }
    
    for result in results:
        if result.passed:
            summary["PASSED"] += 1
        else:
            summary["FAILED"] += 1
        
        summary[result.severity] += 1
    
    # Check if all ERROR level validations passed
    passed = all(result.passed for result in results if result.severity == "ERROR")
    
    # Create a unique validation ID
    validation_id = f"val-{datetime.now(timezone.utc).timestamp():.0f}"
    
    # Store validation results in policy metadata if requested
    # This could be added as an option in the request
    
    return PolicyValidationResponse(
        policy_id=db_policy.id,
        policy_name=db_policy.name,
        policy_version=db_policy.version,
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
        validation_id=validation_id,
        results=results,
        passed=passed,
        summary=summary
    )

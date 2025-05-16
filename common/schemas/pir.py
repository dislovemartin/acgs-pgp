from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator, FilePath
from datetime import datetime, timezone
import uuid

class PolicyStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_VALIDATION = "PENDING_VALIDATION"
    PENDING_FV = "PENDING_FV"  # Formal Verification
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"

class PolicySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TriggerConditionType(str, Enum):
    PROMPT_PATTERN = "prompt_pattern"
    CONTEXT_ATTRIBUTE = "context_attribute"  # Corresponds to ContextAttributeMatcher
    TOOL_USAGE_REQUEST = "tool_usage_request"  # Corresponds to ToolUsageMatcher
    RESPONSE_PATTERN = "response_pattern"
    ANOMALY_SCORE = "anomaly_score"  # New
    CONTENT_ANALYSIS = "content_analysis"  # Keep for backward compatibility
    METADATA_MATCH = "metadata_match"  # Keep for backward compatibility
    CUSTOM = "custom"

class GovernanceActionType(str, Enum):
    ALLOW = "ALLOW"  # New, for explicit allow
    BLOCK = "BLOCK"  # Existing: block_execution
    REDACT_PROMPT = "REDACT_PROMPT"  # New
    REDACT_RESPONSE = "REDACT_RESPONSE"  # Existing: redact (general)
    TRANSFORM_PROMPT_PREPEND = "TRANSFORM_PROMPT_PREPEND"  # New
    TRANSFORM_PROMPT_APPEND = "TRANSFORM_PROMPT_APPEND"  # New
    TRANSFORM_PROMPT_REPLACE = "TRANSFORM_PROMPT_REPLACE"  # New
    TRANSFORM_RESPONSE_PREPEND = "TRANSFORM_RESPONSE_PREPEND"  # New
    TRANSFORM_RESPONSE_APPEND = "TRANSFORM_RESPONSE_APPEND"  # New
    LOG_EVENT = "LOG_EVENT"  # Existing: log_action
    ALERT_ADMINS = "ALERT_ADMINS"  # New
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"  # Existing: require_approval
    INVOKE_SECURE_GOVERNANCE_TOOL = "INVOKE_SECURE_GOVERNANCE_TOOL"  # New
    INITIATE_SMPC_PROTOCOL = "INITIATE_SMPC_PROTOCOL"  # New
    OVERRIDE_LLM_RESPONSE = "OVERRIDE_LLM_RESPONSE"  # New
    MODIFY_PROMPT = "modify_prompt"  # Kept for backward compatibility
    BLOCK_EXECUTION = "block_execution"  # Kept for backward compatibility
    REQUIRE_APPROVAL = "require_approval"  # Kept for backward compatibility
    LOG_ACTION = "log_action"  # Kept for backward compatibility
    APPLY_TEMPLATE = "apply_template"  # Kept for backward compatibility
    REDACT = "redact"  # Kept for backward compatibility
    NOTIFY = "notify"  # Kept for backward compatibility
    CUSTOM = "custom"  # Kept for backward compatibility
    CUSTOM_ACTION = "CUSTOM_ACTION"  # Renamed from "custom" for clarity

class ScopeModelInclusionType(str, Enum):
    ALL = "all"
    INCLUDE = "include"
    EXCLUDE = "exclude"

class ScopeUserRoleInclusionType(str, Enum):
    ALL = "all"
    INCLUDE = "include"
    EXCLUDE = "exclude"

class ScopeApplicationInclusionType(str, Enum):
    ALL = "all"
    INCLUDE = "include"
    EXCLUDE = "exclude"

class ScopeDataSensitivityInclusionType(str, Enum):
    ALL = "all"
    INCLUDE = "include"
    EXCLUDE = "exclude"
    MINIMUM = "minimum"

class Scope(BaseModel):
    """Defines the applicability of the policy."""
    llm_models_inclusion: ScopeModelInclusionType = ScopeModelInclusionType.ALL
    llm_models_list: List[str] = Field(default_factory=list)
    user_roles_inclusion: ScopeUserRoleInclusionType = ScopeUserRoleInclusionType.ALL
    user_roles_list: List[str] = Field(default_factory=list)
    applications_inclusion: ScopeApplicationInclusionType = ScopeApplicationInclusionType.ALL
    applications_list: List[str] = Field(default_factory=list)
    data_sensitivity_inclusion: ScopeDataSensitivityInclusionType = ScopeDataSensitivityInclusionType.ALL
    data_sensitivity_levels: List[str] = Field(default_factory=list)
    custom_scope_attributes: Dict[str, Any] = Field(default_factory=dict)

class PromptPattern(BaseModel):
    """Pattern to match in the input prompt."""
    pattern: str
    is_regex: bool = False
    case_sensitive: bool = False
    description: Optional[str] = None


class PromptPatternMatcher(BaseModel):
    """Enhanced pattern matcher for input prompts."""
    pattern_type: str = Field(..., description="Matching algorithm: REGEX, KEYWORD_LIST, SEMANTIC_SIMILARITY")  # Enum: ["REGEX", "KEYWORD_LIST", "SEMANTIC_SIMILARITY"]
    value: Union[str, List[str]]
    case_sensitive: bool = Field(default=False, alias="matchCase")  # Alias for schema compatibility
    similarity_threshold: Optional[float] = None
    embedding_model_id: Optional[str] = None
    description: Optional[str] = None

class ContextAttribute(BaseModel):
    """Context attribute to match."""
    attribute_name: str
    attribute_value: Any
    match_type: str = "exact"  # exact, contains, regex, greater_than, less_than, etc.
    description: Optional[str] = None

class ToolUsageRequest(BaseModel):
    """Tool usage request to match."""
    tool_name: str
    parameter_constraints: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class ResponsePattern(BaseModel):
    """Pattern to match in the response."""
    pattern: str
    is_regex: bool = False
    case_sensitive: bool = False
    description: Optional[str] = None


class AnomalyScoreMatcher(BaseModel):
    """Matcher for anomaly scores from detection systems."""
    source: str = Field(..., description="Source of anomaly score")  # Enum: ["INFERENCE_GATEWAY_ISOLATION_FOREST", "CUSTOM_DETECTOR"]
    score_operator: str = Field(..., description="Comparison operator")  # Enum: ["GT", "GTE"]
    threshold: float
    description: Optional[str] = None

class TriggerConditions(BaseModel):
    """Structured representation of conditions that activate the policy."""
    prompt_patterns: List[PromptPattern] = Field(default_factory=list)  # Legacy format
    context_attributes: List[ContextAttribute] = Field(default_factory=list)  # Legacy format
    tool_usage_requests: List[ToolUsageRequest] = Field(default_factory=list)  # Legacy format
    response_patterns: List[ResponsePattern] = Field(default_factory=list)  # Legacy format
    custom_conditions: List[Dict[str, Any]] = Field(default_factory=list)
    condition_logic: str = "ANY"  # ANY, ALL, CUSTOM
    custom_logic_expression: Optional[str] = None
    
    # New v2 fields
    operator: str = Field(default="AND", description="Logic for combining conditions: AND or OR")  # Changed from condition_logic
    conditions: List[Union[PromptPatternMatcher, ContextAttribute, ToolUsageRequest, ResponsePattern, AnomalyScoreMatcher]] = Field(default_factory=list)

class TriggerCondition(BaseModel):
    """Legacy trigger condition model for backward compatibility."""
    condition_type: TriggerConditionType
    parameters: Dict[str, Any]
    description: Optional[str] = None

    @validator('parameters')
    def validate_parameters(cls, v, values):
        condition_type = values.get('condition_type')
        if condition_type == TriggerConditionType.PROMPT_PATTERN:
            if 'patterns' not in v or not isinstance(v['patterns'], list):
                raise ValueError("Prompt pattern condition requires 'patterns' list")
        elif condition_type == TriggerConditionType.TOOL_USAGE:
            if 'tool_names' not in v or not isinstance(v['tool_names'], list):
                raise ValueError("Tool usage condition requires 'tool_names' list")
        return v

class GovernanceAction(BaseModel):
    """Action to take when conditions are met."""
    action_type: GovernanceActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 0
    execution_order: int = Field(default=0, description="Defines sequence if multiple actions")  # New
    description: Optional[str] = None

    @validator('parameters')
    def validate_action_parameters(cls, v, values):
        action_type = values.get('action_type')
        if action_type == GovernanceActionType.MODIFY_PROMPT:
            if 'modifications' not in v or not isinstance(v['modifications'], list):
                raise ValueError("Modify prompt action requires 'modifications' list")
        return v

class ApprovalMetadata(BaseModel):
    """Metadata for approval history."""
    approved_by: str
    approved_at: datetime
    comments: Optional[str] = None

class SynthesisMetadata(BaseModel):
    """Metadata for synthesis details."""
    synthesized_by: str
    synthesized_at: datetime
    source_type: str  # manual, llm, imported
    source_details: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None

class LTLSpecification(BaseModel):
    """Linear Temporal Logic specification for formal verification."""
    property_id: str = Field(..., description="Unique ID for this LTL property.")
    formula: str = Field(..., description="The LTL formula.")
    description: Optional[str] = None
    variables_mapping: Optional[Dict[str, str]] = Field(default_factory=dict, description="Maps LTL variables to P-IR context/action fields.")


class TemporalLogicAnnotations(BaseModel):
    """Temporal logic annotations for formal verification."""
    ltl_specifications: List[LTLSpecification] = Field(default_factory=list)
    # ctl_specifications: List[CTLSpecification] = Field(default_factory=list)  # Add if CTL is also desired


class HomomorphicEncryptionPolicy(BaseModel):
    """Policy for homomorphic encryption of P-IR fields."""
    fields_to_encrypt: List[str] = Field(default_factory=list, description="JSONPath to fields within this P-IR to be HE encrypted.")
    he_scheme_id: Optional[str] = None
    key_management_policy_id: Optional[str] = None


class QuantumOptimizationHints(BaseModel):
    """Hints for quantum optimization of policy evaluation."""
    qubo_formulation_hint: Optional[str] = None
    target_objective: Optional[str] = None


class PQCSignature(BaseModel):
    """Post-Quantum Cryptography signature for the P-IR."""
    algorithm: Optional[str] = None  # e.g., "CRYSTALS-Dilithium2"
    signature_value: Optional[str] = None  # Base64 encoded
    public_key_id: Optional[str] = None


class FormalVerificationStatus(BaseModel):
    """Status of formal verification for the P-IR."""
    last_run_id: Optional[str] = None
    status: Optional[str] = None  # e.g., "NOT_VERIFIED", "VERIFIED", "FALSIFIED"
    verified_timestamp_utc: Optional[datetime] = None
    verified_properties: List[str] = Field(default_factory=list)


class PIRMetadata(BaseModel):
    """Metadata for the policy."""
    author: Optional[str] = None
    created_timestamp: Optional[datetime] = None
    last_updated_timestamp: Optional[datetime] = None
    approval_history: List[ApprovalMetadata] = Field(default_factory=list)
    synthesis_details: Optional[SynthesisMetadata] = None
    compliance_standards: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # New fields based on pir_v2.schema.json
    pqc_signature: Optional[PQCSignature] = None
    formal_verification: Optional[FormalVerificationStatus] = None

class PIRBase(BaseModel):
    """Base class for PIR schemas."""
    name: str
    description: str
    status: PolicyStatus = PolicyStatus.DRAFT
    constitutional_references: List[str] = Field(default_factory=list)
    scope: Scope = Field(default_factory=Scope)
    # Support both legacy trigger_conditions and new structured trigger_conditions
    trigger_conditions: Union[List[TriggerCondition], TriggerConditions] = Field(...)
    governance_actions: List[GovernanceAction] = Field(...)
    severity: PolicySeverity = PolicySeverity.MEDIUM
    priority: int = 50  # 0-100, higher is more important
    tags: List[str] = Field(default_factory=list)
    created_by: str = "system"
    updated_by: str = "system"
    metadata: Union[Dict[str, Any], PIRMetadata] = Field(default_factory=dict)
    
    # New v2 fields
    source_regulation_references: List[Dict[str, str]] = Field(default_factory=list)  # Example: [{"sourceId": "GDPR Art. 5", "jurisdiction": "EU"}]
    temporal_logic_annotations: Optional[TemporalLogicAnnotations] = None
    homomorphic_encryption_policy: Optional[HomomorphicEncryptionPolicy] = None
    quantum_optimization_hints: Optional[QuantumOptimizationHints] = None

class PIRCreate(PIRBase):
    """Schema for creating a new PIR."""
    version: int = 1

class PIRUpdate(BaseModel):
    """Schema for updating an existing PIR."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PolicyStatus] = None
    constitutional_references: Optional[List[str]] = None
    scope: Optional[Scope] = None
    trigger_conditions: Optional[Union[List[TriggerCondition], TriggerConditions]] = None
    governance_actions: Optional[List[GovernanceAction]] = None
    severity: Optional[PolicySeverity] = None
    priority: Optional[int] = None
    tags: Optional[List[str]] = None
    updated_by: Optional[str] = None
    metadata: Optional[Union[Dict[str, Any], PIRMetadata]] = None

class PIR(PIRBase):
    """Policy Intermediate Representation (P-IR) schema."""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version_id: Optional[str] = None  # New field: e.g., pirId_vX.Y.Z

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "policy_id": "550e8400-e29b-41d4-a716-446655440000",
                "version": 1,
                "name": "Prevent PII Disclosure",
                "description": "Prevents sharing of personally identifiable information",
                "status": "active",
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
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "created_by": "system@acgs-pgp.local",
                "updated_by": "system@acgs-pgp.local",
                "tags": ["security", "compliance", "pii"],
                "version_id": "550e8400-e29b-41d4-a716-446655440000_v1.0.0",
                "source_regulation_references": [{"sourceId": "EU AI Act Article 10", "jurisdiction": "EU"}],
                "temporal_logic_annotations": {
                    "ltl_specifications": [{
                        "property_id": "safety-prop-001",
                        "formula": "G (input_is_harmful -> !output_is_generated)",
                        "description": "Globally, if input is harmful, no output should be generated."
                    }]
                },
                "homomorphic_encryption_policy": {
                    "fields_to_encrypt": ["$.trigger_conditions.prompt_patterns[*].pattern"],
                    "he_scheme_id": "BFV-128",
                    "key_management_policy_id": "key-policy-001"
                },
                "quantum_optimization_hints": {
                    "qubo_formulation_hint": "policy_evaluation_latency_optimization",
                    "target_objective": "minimize_false_negatives"
                },
                "metadata": {
                    "author": "compliance-team",
                    "created_timestamp": "2023-01-01T00:00:00",
                    "last_updated_timestamp": "2023-01-01T00:00:00",
                    "approval_history": [
                        {
                            "approved_by": "compliance-officer",
                            "approved_at": "2023-01-01T12:00:00",
                            "comments": "Approved after review"
                        }
                    ],
                    "synthesis_details": {
                        "synthesized_by": "gpt-4",
                        "synthesized_at": "2023-01-01T00:00:00",
                        "source_type": "llm",
                        "source_details": {
                            "prompt": "Create a policy to prevent PII disclosure"
                        },
                        "confidence_score": 0.95
                    },
                    "compliance_standards": ["GDPR", "CCPA"],
                    "custom_metadata": {
                        "business_unit": "customer_service"
                    },
                    "pqc_signature": {
                        "algorithm": "CRYSTALS-Dilithium2",
                        "signature_value": "base64encodedvalue...",
                        "public_key_id": "key_id_123"
                    },
                    "formal_verification": {
                        "status": "VERIFIED",
                        "last_run_id": "fv-run-123",
                        "verified_timestamp_utc": "2023-01-02T10:30:00",
                        "verified_properties": ["safety-prop-001"]
                    }
                }
            }
        }

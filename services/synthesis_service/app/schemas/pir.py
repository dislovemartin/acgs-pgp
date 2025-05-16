from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
import sys
import os

# Import the common PIR schema
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from common.schemas.pir import (
    PIR, TriggerCondition, GovernanceAction, PolicyStatus, PolicySeverity, Scope,
    TriggerConditions, PromptPattern, ContextAttribute, ToolUsageRequest,
    ResponsePattern, TriggerConditionType, GovernanceActionType, PIRMetadata,
    SynthesisMetadata, ApprovalMetadata, ScopeModelInclusionType, ScopeUserRoleInclusionType,
    ScopeApplicationInclusionType, ScopeDataSensitivityInclusionType
)

class PolicySynthesisRequest(BaseModel):
    policy_intent: str = Field(..., description="Natural language description of the desired policy")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context for policy generation"
    )
    constraints: Optional[List[str]] = Field(
        default_factory=list,
        description="List of constraints to apply during policy generation"
    )
    examples: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Example policies for few-shot learning"
    )

class PolicySynthesisResponse(BaseModel):
    policy: PIR
    explanation: str = Field(..., description="Explanation of the generated policy")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the generated policy (0.0 to 1.0)"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Any warnings or issues with the generated policy"
    )

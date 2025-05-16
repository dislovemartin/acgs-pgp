from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import time

from ....engine.policy_evaluator import PolicyEvaluator, EvaluationResult
from ....core.config import get_settings
from ....core.rge import get_policy_evaluator

router = APIRouter()

class EvaluationRequest(BaseModel):
    prompt: str
    metadata: Optional[Dict[str, Any]] = None

class EvaluationResponse(BaseModel):
    result: str
    allowed: bool
    modified_prompt: Optional[str] = None
    triggered_policies: List[Dict[str, Any]] = []
    evaluation_time_ms: float

# Models for batch evaluation
class BatchEvaluationPrompt(BaseModel):
    id: str = Field(..., description="Unique identifier for this prompt within the batch")
    text: str = Field(..., description="The prompt text to evaluate")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata for policy evaluation")

class BatchEvaluationRequest(BaseModel):
    prompts: List[BatchEvaluationPrompt] = Field(..., description="List of prompts to evaluate")

class BatchEvaluationResultItem(BaseModel):
    id: str = Field(..., description="ID matching the input prompt")
    result: str = Field(..., description="Evaluation result: ALLOW, MODIFY, BLOCK, or REQUIRE_APPROVAL")
    allowed: bool = Field(..., description="Whether the prompt is allowed (true for ALLOW or MODIFY)")
    modified_prompt: Optional[str] = Field(default=None, description="Modified prompt if result is MODIFY")
    triggered_policies: List[Dict[str, Any]] = Field(default_factory=list, description="Policies that were triggered")
    blocked: bool = Field(..., description="Whether the prompt was blocked")
    requires_approval: bool = Field(..., description="Whether the prompt requires approval")

class BatchEvaluationResponse(BaseModel):
    results: List[BatchEvaluationResultItem] = Field(..., description="Evaluation results for each prompt")
    evaluation_time_ms: float = Field(..., description="Total evaluation time in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp when the evaluation was completed")

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_prompt(
    request: EvaluationRequest,
    evaluator: PolicyEvaluator = Depends(get_policy_evaluator)
):
    """
    Evaluate a prompt against all active policies.
    
    This endpoint checks if the provided prompt complies with the active governance policies.
    It can return:
    - ALLOW: The prompt is compliant and can be processed as-is
    - MODIFY: The prompt was modified to be compliant
    - BLOCK: The prompt violates a blocking policy
    - REQUIRE_APPROVAL: The prompt requires manual approval
    """
    start_time = time.time()
    result, evaluations, modified_prompt = evaluator.evaluate_prompt(
        prompt=request.prompt,
        metadata=request.metadata or {}
    )
    end_time = time.time()
    
    # Convert evaluations to serializable format
    triggered_policies = []
    for eval_ in evaluations:
        triggered_policies.append({
            "policy_id": eval_.policy.policy_id,
            "policy_name": eval_.policy.name,
            "matched_condition": eval_.matched_condition,
            "applied_actions": [
                {"action_type": action.action_type, "parameters": action.parameters}
                for action, _ in eval_.applied_actions
            ]
        })
    
    return EvaluationResponse(
        result=result.value,
        allowed=result in [EvaluationResult.ALLOW, EvaluationResult.MODIFY],
        modified_prompt=modified_prompt if result == EvaluationResult.MODIFY else None,
        triggered_policies=triggered_policies,
        evaluation_time_ms=(end_time - start_time) * 1000
    )

@router.post("/evaluate/batch", response_model=BatchEvaluationResponse)
async def batch_evaluate_prompts(
    request: BatchEvaluationRequest,
    evaluator: PolicyEvaluator = Depends(get_policy_evaluator)
):
    """
    Evaluate multiple prompts against all active policies in a single request.
    
    This endpoint processes a batch of prompts and returns evaluation results for each one.
    For each prompt, the result can be:
    - ALLOW: The prompt is compliant and can be processed as-is
    - MODIFY: The prompt was modified to be compliant
    - BLOCK: The prompt violates a blocking policy
    - REQUIRE_APPROVAL: The prompt requires manual approval
    """
    start_time = time.time()
    batch_results = []
    
    for item in request.prompts:
        # Evaluate each prompt using the existing evaluation logic
        result_enum, evaluations, modified_text = evaluator.evaluate_prompt(
            prompt=item.text,
            metadata=item.metadata or {}
        )
        
        # Process the evaluation results for this prompt
        triggered_policies = []
        for eval_item in evaluations:
            triggered_policies.append({
                "policy_id": eval_item.policy.policy_id,
                "policy_name": eval_item.policy.name,
                "matched_condition": eval_item.matched_condition,
                "applied_actions": [
                    {"action_type": action.action_type, "parameters": action.parameters}
                    for action, _ in eval_item.applied_actions
                ]
            })
        
        # Add the result for this prompt to the batch results
        batch_results.append(BatchEvaluationResultItem(
            id=item.id,
            result=result_enum.value,
            allowed=result_enum in [EvaluationResult.ALLOW, EvaluationResult.MODIFY],
            modified_prompt=modified_text if result_enum == EvaluationResult.MODIFY else None,
            triggered_policies=triggered_policies,
            blocked=result_enum == EvaluationResult.BLOCK,
            requires_approval=result_enum == EvaluationResult.REQUIRE_APPROVAL
        ))
    
    end_time = time.time()
    evaluation_time_ms = (end_time - start_time) * 1000
    
    return BatchEvaluationResponse(
        results=batch_results,
        evaluation_time_ms=evaluation_time_ms,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@router.get("/policies/active", response_model=List[Dict[str, Any]])
async def list_active_policies(
    evaluator: PolicyEvaluator = Depends(get_policy_evaluator)
):
    """List all active policies currently loaded in the RGE."""
    return [
        {
            "policy_id": p.policy_id,
            "name": p.name,
            "version": p.version,
            "description": p.description,
            "trigger_conditions": [c.dict() for c in p.trigger_conditions],
            "governance_actions": [a.dict() for a in p.governance_actions]
        }
        for p in evaluator.active_policies
    ]

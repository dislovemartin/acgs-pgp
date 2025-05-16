from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ....db.base import get_db
from ....crud import pir as crud_pir
from common.schemas.pir import PIR

router = APIRouter()

class BulkPolicyRequest(BaseModel):
    """Request model for bulk policy retrieval."""
    policy_ids: List[str] = Field(..., description="List of policy IDs to retrieve")
    include_archived: bool = Field(False, description="Whether to include archived policies")
    include_superseded: bool = Field(False, description="Whether to include superseded policies")

class BulkPolicyResponse(BaseModel):
    """Response model for bulk policy retrieval."""
    policies: Dict[str, Optional[PIR]] = Field(..., description="Map of policy ID to policy data")
    not_found: List[str] = Field(default_factory=list, description="List of policy IDs that were not found")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the request")

@router.post("/bulk/get", response_model=BulkPolicyResponse)
def get_policies_bulk(
    request: BulkPolicyRequest,
    db: Session = Depends(get_db)
):
    """
    Retrieve multiple policies by their IDs in a single request.
    
    This endpoint allows fetching multiple policies at once, which is more efficient
    than making separate requests for each policy. The response includes a mapping
    of policy IDs to their data, as well as a list of IDs that were not found.
    """
    result = {}
    not_found = []
    
    # Process each policy ID in the request
    for policy_id in request.policy_ids:
        policy = crud_pir.get_policy(db, policy_id=policy_id)
        
        if policy is None:
            not_found.append(policy_id)
            result[policy_id] = None
            continue
            
        # Skip archived or superseded policies if not explicitly requested
        if policy.status == "ARCHIVED" and not request.include_archived:
            not_found.append(policy_id)
            result[policy_id] = None
            continue
            
        if policy.status == "SUPERSEDED" and not request.include_superseded:
            not_found.append(policy_id)
            result[policy_id] = None
            continue
            
        # Convert the policy to a dictionary and add it to the result
        result[policy_id] = policy.to_dict()
    
    return BulkPolicyResponse(
        policies=result,
        not_found=not_found,
        metadata={
            "total_requested": len(request.policy_ids),
            "total_found": len(request.policy_ids) - len(not_found),
            "include_archived": request.include_archived,
            "include_superseded": request.include_superseded
        }
    )

class BulkPolicyStatusRequest(BaseModel):
    """Request model for bulk policy status check."""
    policy_ids: List[str] = Field(..., description="List of policy IDs to check")

class PolicyStatusInfo(BaseModel):
    """Information about a policy's status."""
    policy_id: str = Field(..., description="Policy ID")
    exists: bool = Field(..., description="Whether the policy exists")
    status: Optional[str] = Field(None, description="Current status of the policy if it exists")
    name: Optional[str] = Field(None, description="Name of the policy if it exists")
    version: Optional[int] = Field(None, description="Version of the policy if it exists")
    version_id: Optional[str] = Field(None, description="Version ID of the policy if it exists")

class BulkPolicyStatusResponse(BaseModel):
    """Response model for bulk policy status check."""
    statuses: List[PolicyStatusInfo] = Field(..., description="Status information for each requested policy")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the request")

@router.post("/bulk/status", response_model=BulkPolicyStatusResponse)
def check_policies_status_bulk(
    request: BulkPolicyStatusRequest,
    db: Session = Depends(get_db)
):
    """
    Check the status of multiple policies by their IDs in a single request.
    
    This endpoint allows checking if policies exist and their current status,
    which is more efficient than making separate requests for each policy.
    """
    statuses = []
    
    # Process each policy ID in the request
    for policy_id in request.policy_ids:
        policy = crud_pir.get_policy(db, policy_id=policy_id)
        
        if policy is None:
            statuses.append(PolicyStatusInfo(
                policy_id=policy_id,
                exists=False,
                status=None,
                name=None,
                version=None,
                version_id=None
            ))
        else:
            statuses.append(PolicyStatusInfo(
                policy_id=policy_id,
                exists=True,
                status=policy.status,
                name=policy.name,
                version=policy.version,
                version_id=policy.version_id
            ))
    
    return BulkPolicyStatusResponse(
        statuses=statuses,
        metadata={
            "total_requested": len(request.policy_ids),
            "total_found": sum(1 for status in statuses if status.exists)
        }
    )

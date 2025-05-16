from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pydantic import BaseModel

from ....db.base import get_db
from ....crud import pir as crud_pir

# Import the common schemas
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))
from common.schemas.pir import PIR, PolicyStatus

router = APIRouter()

class StatusTransitionResponse(BaseModel):
    """Response model for status transition endpoints."""
    policy: PIR
    transition_message: str
    previous_status: str


@router.post("/{policy_id}/submit_for_validation", response_model=StatusTransitionResponse)
def submit_policy_for_validation(
    policy_id: str,
    comments: Dict[str, Any] = Body({"comments": "Submitted for validation"}),
    db: Session = Depends(get_db)
):
    """
    Submit a policy for validation (DRAFT -> PENDING_VALIDATION).
    """
    db_policy = crud_pir.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Check current status
    if db_policy.status != PolicyStatus.DRAFT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy must be in DRAFT status to submit for validation. Current status: {db_policy.status}"
        )
    
    previous_status = db_policy.status
    
    # Update the policy status
    update_data = {
        "status": PolicyStatus.PENDING_VALIDATION.value,
        "updated_by": comments.get("user", "system"),
        "metadata": {
            **(db_policy.metadata_ or {}),
            "validation_request": {
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "comments": comments.get("comments", "")
            }
        }
    }
    
    updated_policy = crud_pir.update_policy(db, db_policy, update_data)
    
    return StatusTransitionResponse(
        policy=updated_policy.to_dict(),
        transition_message=f"Policy submitted for validation: {comments.get('comments', '')}",
        previous_status=previous_status
    )


@router.post("/{policy_id}/approve_validation", response_model=StatusTransitionResponse)
def approve_validation(
    policy_id: str,
    approval_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Approve a policy validation (PENDING_VALIDATION -> ACTIVE or PENDING_FV).
    
    If formal_verification is required in the approval_data, the policy will be moved to PENDING_FV status.
    Otherwise, it will be moved directly to ACTIVE status.
    """
    db_policy = crud_pir.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Check current status
    if db_policy.status != PolicyStatus.PENDING_VALIDATION.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy must be in PENDING_VALIDATION status to approve. Current status: {db_policy.status}"
        )
    
    previous_status = db_policy.status
    
    # Determine the next status based on whether formal verification is required
    require_formal_verification = approval_data.get("require_formal_verification", False)
    next_status = PolicyStatus.PENDING_FV.value if require_formal_verification else PolicyStatus.ACTIVE.value
    
    # Create approval metadata
    approval_metadata = {
        "approved_by": approval_data.get("user", "system"),
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "comments": approval_data.get("comments", "Validation approved"),
        "require_formal_verification": require_formal_verification
    }
    
    # Update the policy metadata to include the approval
    current_metadata = db_policy.metadata_ or {}
    approval_history = current_metadata.get("approval_history", [])
    approval_history.append(approval_metadata)
    
    # Update the policy
    update_data = {
        "status": next_status,
        "updated_by": approval_data.get("user", "system"),
        "metadata": {
            **current_metadata,
            "approval_history": approval_history
        }
    }
    
    updated_policy = crud_pir.update_policy(db, db_policy, update_data)
    
    # Create the response
    transition_message = "Policy validation approved and moved to ACTIVE status."
    if require_formal_verification:
        transition_message = "Policy validation approved and moved to PENDING_FV status for formal verification."
    
    return StatusTransitionResponse(
        policy=updated_policy.to_dict(),
        transition_message=transition_message,
        previous_status=previous_status
    )


@router.post("/{policy_id}/reject_validation", response_model=StatusTransitionResponse)
def reject_validation(
    policy_id: str,
    rejection_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Reject a policy validation (PENDING_VALIDATION -> REJECTED or DRAFT).
    
    If return_to_draft is True in the rejection_data, the policy will be moved back to DRAFT status.
    Otherwise, it will be moved to REJECTED status.
    """
    db_policy = crud_pir.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Check current status
    if db_policy.status != PolicyStatus.PENDING_VALIDATION.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy must be in PENDING_VALIDATION status to reject. Current status: {db_policy.status}"
        )
    
    previous_status = db_policy.status
    
    # Determine the next status based on whether to return to draft
    return_to_draft = rejection_data.get("return_to_draft", False)
    next_status = PolicyStatus.DRAFT.value if return_to_draft else PolicyStatus.REJECTED.value
    
    # Create rejection metadata
    rejection_metadata = {
        "rejected_by": rejection_data.get("user", "system"),
        "rejected_at": datetime.now(timezone.utc).isoformat(),
        "comments": rejection_data.get("comments", "Validation rejected"),
        "return_to_draft": return_to_draft
    }
    
    # Update the policy metadata to include the rejection
    current_metadata = db_policy.metadata_ or {}
    rejection_history = current_metadata.get("rejection_history", [])
    rejection_history.append(rejection_metadata)
    
    # Update the policy
    update_data = {
        "status": next_status,
        "updated_by": rejection_data.get("user", "system"),
        "metadata": {
            **current_metadata,
            "rejection_history": rejection_history
        }
    }
    
    updated_policy = crud_pir.update_policy(db, db_policy, update_data)
    
    # Create the response
    transition_message = "Policy validation rejected and moved to REJECTED status."
    if return_to_draft:
        transition_message = "Policy validation rejected and returned to DRAFT status for revision."
    
    return StatusTransitionResponse(
        policy=updated_policy.to_dict(),
        transition_message=transition_message,
        previous_status=previous_status
    )


@router.post("/{policy_id}/complete_formal_verification", response_model=StatusTransitionResponse)
def complete_formal_verification(
    policy_id: str,
    verification_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Complete formal verification for a policy (PENDING_FV -> ACTIVE or REJECTED).
    
    If verification_passed is True, the policy will be moved to ACTIVE status.
    Otherwise, it will be moved to REJECTED status or back to DRAFT if return_to_draft is True.
    """
    db_policy = crud_pir.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Check current status
    if db_policy.status != PolicyStatus.PENDING_FV.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy must be in PENDING_FV status to complete verification. Current status: {db_policy.status}"
        )
    
    previous_status = db_policy.status
    
    # Determine the next status based on verification result
    verification_passed = verification_data.get("verification_passed", False)
    return_to_draft = verification_data.get("return_to_draft", False) and not verification_passed
    
    if verification_passed:
        next_status = PolicyStatus.ACTIVE.value
    else:
        next_status = PolicyStatus.DRAFT.value if return_to_draft else PolicyStatus.REJECTED.value
    
    # Create formal verification metadata
    verification_metadata = {
        "verified_by": verification_data.get("user", "system"),
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "verification_passed": verification_passed,
        "comments": verification_data.get("comments", ""),
        "verified_properties": verification_data.get("verified_properties", []),
        "failed_properties": verification_data.get("failed_properties", []),
        "verification_run_id": verification_data.get("verification_run_id", f"fv-run-{datetime.now(timezone.utc).timestamp()}")
    }
    
    # Update the policy metadata
    current_metadata = db_policy.metadata_ or {}
    formal_verification = {
        "status": "VERIFIED" if verification_passed else "FALSIFIED",
        "last_run_id": verification_metadata["verification_run_id"],
        "verified_timestamp_utc": verification_metadata["verified_at"],
        "verified_properties": verification_metadata["verified_properties"]
    }
    
    verification_history = current_metadata.get("verification_history", [])
    verification_history.append(verification_metadata)
    
    # Update the policy
    update_data = {
        "status": next_status,
        "updated_by": verification_data.get("user", "system"),
        "metadata": {
            **current_metadata,
            "verification_history": verification_history,
            "formal_verification": formal_verification
        }
    }
    
    updated_policy = crud_pir.update_policy(db, db_policy, update_data)
    
    # Create the response
    if verification_passed:
        transition_message = "Formal verification completed successfully. Policy is now ACTIVE."
    elif return_to_draft:
        transition_message = "Formal verification failed. Policy returned to DRAFT for revision."
    else:
        transition_message = "Formal verification failed. Policy marked as REJECTED."
    
    return StatusTransitionResponse(
        policy=updated_policy.to_dict(),
        transition_message=transition_message,
        previous_status=previous_status
    )


@router.post("/{policy_id}/archive", response_model=StatusTransitionResponse)
def archive_policy(
    policy_id: str,
    archive_data: Dict[str, Any] = Body({"comments": "Policy archived"}),
    db: Session = Depends(get_db)
):
    """
    Archive a policy (ACTIVE -> ARCHIVED).
    """
    db_policy = crud_pir.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Check current status
    if db_policy.status != PolicyStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy must be in ACTIVE status to archive. Current status: {db_policy.status}"
        )
    
    previous_status = db_policy.status
    
    # Create archive metadata
    archive_metadata = {
        "archived_by": archive_data.get("user", "system"),
        "archived_at": datetime.now(timezone.utc).isoformat(),
        "comments": archive_data.get("comments", "Policy archived")
    }
    
    # Update the policy metadata
    current_metadata = db_policy.metadata_ or {}
    
    # Update the policy
    update_data = {
        "status": PolicyStatus.ARCHIVED.value,
        "updated_by": archive_data.get("user", "system"),
        "metadata": {
            **current_metadata,
            "archive_metadata": archive_metadata
        }
    }
    
    updated_policy = crud_pir.update_policy(db, db_policy, update_data)
    
    return StatusTransitionResponse(
        policy=updated_policy.to_dict(),
        transition_message=f"Policy archived: {archive_data.get('comments', '')}",
        previous_status=previous_status
    )


@router.post("/{policy_id}/supersede", response_model=StatusTransitionResponse)
def supersede_policy(
    policy_id: str,
    supersede_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Mark a policy as superseded by a newer version (ACTIVE -> SUPERSEDED).
    
    Requires the ID of the policy that supersedes this one.
    """
    db_policy = crud_pir.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Check current status
    if db_policy.status != PolicyStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy must be in ACTIVE status to be superseded. Current status: {db_policy.status}"
        )
    
    # Verify the superseding policy exists
    superseded_by_id = supersede_data.get("superseded_by_id")
    if not superseded_by_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="superseded_by_id is required"
        )
    
    superseding_policy = crud_pir.get_policy(db, policy_id=superseded_by_id)
    if not superseding_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Superseding policy with ID {superseded_by_id} not found"
        )
    
    previous_status = db_policy.status
    
    # Create superseded metadata
    superseded_metadata = {
        "superseded_by": superseding_policy.id,
        "superseded_by_version": superseding_policy.version,
        "superseded_by_version_id": superseding_policy.version_id,
        "superseded_at": datetime.now(timezone.utc).isoformat(),
        "superseded_by_user": supersede_data.get("user", "system"),
        "comments": supersede_data.get("comments", "Policy superseded by newer version")
    }
    
    # Update the policy metadata
    current_metadata = db_policy.metadata_ or {}
    
    # Update the policy
    update_data = {
        "status": PolicyStatus.SUPERSEDED.value,
        "updated_by": supersede_data.get("user", "system"),
        "metadata": {
            **current_metadata,
            "superseded_metadata": superseded_metadata
        }
    }
    
    updated_policy = crud_pir.update_policy(db, db_policy, update_data)
    
    return StatusTransitionResponse(
        policy=updated_policy.to_dict(),
        transition_message=f"Policy superseded by {superseding_policy.name} (ID: {superseding_policy.id})",
        previous_status=previous_status
    )

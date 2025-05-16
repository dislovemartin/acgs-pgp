from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ....db.base import get_db
from ....crud import pir as crud_pir
from ....models import pir as models

# Import the common schemas - adjust the import path as needed
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))
from common.schemas.pir import PIR, PIRCreate, PIRUpdate, PolicyStatus, PolicySeverity, Scope

router = APIRouter()

@router.post("/", response_model=PIR, status_code=status.HTTP_201_CREATED)
def create_policy(policy: PIRCreate, db: Session = Depends(get_db)):
    """
    Create a new policy.
    """
    # Check if policy with same name and version already exists
    existing_policy = crud_pir.get_policy_by_name_version(
        db, name=policy.name, version=policy.version
    )
    if existing_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy with name '{policy.name}' and version '{policy.version}' already exists."
        )

    return crud_pir.create_policy(db=db, policy=policy)

@router.get("/", response_model=List[PIR])
def read_policies(
    skip: int = 0,
    limit: int = 100,
    status: Optional[PolicyStatus] = None,
    severity: Optional[PolicySeverity] = None,
    min_priority: Optional[int] = None,
    tags: Optional[List[str]] = Query(None),
    constitutional_references: Optional[List[str]] = Query(None),
    # New v2 filter parameters
    version_id: Optional[str] = None,
    formal_verification_status: Optional[str] = None,
    source_regulation: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve policies with optional filtering by various criteria including new v2 fields.
    """
    # Convert enum values to strings if provided
    status_value = status.value if status else None
    severity_value = severity.value if severity else None

    policies = crud_pir.get_policies(
        db,
        skip=skip,
        limit=limit,
        status=status_value,
        severity=severity_value,
        min_priority=min_priority,
        tags=tags,
        constitutional_references=constitutional_references,
        version_id=version_id,
        formal_verification_status=formal_verification_status,
        source_regulation=source_regulation,
        jurisdiction=jurisdiction
    )
    return policies

@router.get("/{policy_id}", response_model=PIR)
def read_policy(policy_id: str, db: Session = Depends(get_db)):
    """
    Get a specific policy by ID.
    """
    db_policy = crud_pir.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    return db_policy

@router.put("/{policy_id}", response_model=PIR)
def update_policy(
    policy_id: str,
    policy: PIRUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a policy.
    """
    db_policy = crud_pir.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    return crud_pir.update_policy(db=db, db_policy=db_policy, policy_update=policy.dict(exclude_unset=True))

@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(policy_id: str, db: Session = Depends(get_db)):
    """
    Delete a policy.
    """
    success = crud_pir.delete_policy(db, policy_id=policy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    return {"ok": True}

@router.get("/name/{policy_name}", response_model=PIR)
def read_policy_by_name(
    policy_name: str,
    version: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get a policy by name and optional version.
    If version is not provided, returns the latest version.
    """
    db_policy = crud_pir.get_policy_by_name_version(
        db, name=policy_name, version=version
    )
    if db_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    return db_policy

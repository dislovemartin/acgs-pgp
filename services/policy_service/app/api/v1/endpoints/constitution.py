from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....db.base import get_db
from ....crud import constitution as crud_constitution
from ....models import constitution as models

# Import the common schemas - adjust the import path as needed
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))
from common.schemas.constitution import AIConstitution, AIConstitutionCreate, AIConstitutionUpdate

router = APIRouter()

@router.post("/", response_model=AIConstitution, status_code=status.HTTP_201_CREATED)
def create_constitution(constitution: AIConstitutionCreate, db: Session = Depends(get_db)):
    """
    Create a new AI Constitution.
    """
    # Get the latest version to increment
    latest_constitution = crud_constitution.get_latest_constitution(db)
    new_version = 1
    if latest_constitution:
        new_version = latest_constitution.version + 1
    
    # Create a full AIConstitution from the AIConstitutionCreate
    constitution_data = constitution.dict()
    constitution_data["version"] = new_version
    
    # Create the AIConstitution
    constitution_obj = AIConstitution(**constitution_data)
    
    return crud_constitution.create_constitution(db=db, constitution=constitution_obj)

@router.get("/", response_model=List[AIConstitution])
def read_constitutions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all AI Constitutions with pagination.
    """
    constitutions = crud_constitution.get_constitutions(db, skip=skip, limit=limit)
    return constitutions

@router.get("/latest", response_model=AIConstitution)
def read_latest_constitution(db: Session = Depends(get_db)):
    """
    Get the latest version of the AI Constitution.
    """
    constitution = crud_constitution.get_latest_constitution(db)
    if constitution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No AI Constitution found"
        )
    return constitution

@router.get("/{constitution_id}", response_model=AIConstitution)
def read_constitution(constitution_id: str, db: Session = Depends(get_db)):
    """
    Get a specific AI Constitution by ID.
    """
    db_constitution = crud_constitution.get_constitution(db, constitution_id=constitution_id)
    if db_constitution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="AI Constitution not found"
        )
    return db_constitution

@router.put("/{constitution_id}", response_model=AIConstitution)
def update_constitution(
    constitution_id: str, 
    constitution: AIConstitutionUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an AI Constitution.
    """
    db_constitution = crud_constitution.get_constitution(db, constitution_id=constitution_id)
    if db_constitution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="AI Constitution not found"
        )
    
    return crud_constitution.update_constitution(
        db=db, 
        db_constitution=db_constitution, 
        constitution_update=constitution.dict(exclude_unset=True)
    )

@router.delete("/{constitution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_constitution(constitution_id: str, db: Session = Depends(get_db)):
    """
    Delete an AI Constitution.
    """
    success = crud_constitution.delete_constitution(db, constitution_id=constitution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="AI Constitution not found"
        )
    return {"ok": True}

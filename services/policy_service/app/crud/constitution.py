from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from .. import models
# Import the common schemas - adjust the import path as needed
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from common.schemas import constitution as schemas

def get_constitution(db: Session, constitution_id: str) -> Optional[models.constitution.AIConstitutionModel]:
    """Get a specific AI Constitution by ID."""
    return db.query(models.constitution.AIConstitutionModel).filter(models.constitution.AIConstitutionModel.id == constitution_id).first()

def get_constitutions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.constitution.AIConstitutionModel]:
    """Get all AI Constitutions with pagination."""
    return db.query(models.constitution.AIConstitutionModel).order_by(
        models.constitution.AIConstitutionModel.version.desc()
    ).offset(skip).limit(limit).all()

def get_latest_constitution(db: Session) -> Optional[models.constitution.AIConstitutionModel]:
    """Get the latest version of the AI Constitution."""
    return db.query(models.constitution.AIConstitutionModel).order_by(
        models.constitution.AIConstitutionModel.version.desc()
    ).first()

def create_constitution(db: Session, constitution: schemas.AIConstitution) -> models.constitution.AIConstitutionModel:
    """Create a new AI Constitution."""
    # Convert principles to a list of dictionaries
    principles_data = [principle.dict() for principle in constitution.principles]
    
    # Handle metadata
    if isinstance(constitution.metadata, dict):
        metadata = constitution.metadata
    else:
        metadata = constitution.metadata.dict()
    
    db_constitution = models.constitution.AIConstitutionModel(
        id=constitution.id,
        version=constitution.version,
        title=constitution.title,
        description=constitution.description,
        principles=principles_data,
        categories=constitution.categories,
        created_by=constitution.created_by,
        updated_by=constitution.updated_by,
        metadata_=metadata
    )
    db.add(db_constitution)
    db.commit()
    db.refresh(db_constitution)
    return db_constitution

def update_constitution(
    db: Session, 
    db_constitution: models.constitution.AIConstitutionModel, 
    constitution_update: dict
) -> models.constitution.AIConstitutionModel:
    """Update an existing AI Constitution."""
    update_data = constitution_update.copy()
    
    for field, value in update_data.items():
        if field == "principles":
            # Convert principles to a list of dictionaries
            principles_data = [principle.dict() if hasattr(principle, 'dict') else principle for principle in value]
            setattr(db_constitution, field, principles_data)
        elif field != "metadata" and field != "metadata_":
            setattr(db_constitution, field, value)
    
    # Handle metadata update
    if "metadata" in update_data:
        metadata_value = update_data["metadata"]
        db_constitution.metadata_ = metadata_value.dict() if hasattr(metadata_value, 'dict') else metadata_value
    
    # Update version and timestamp
    db_constitution.version += 1
    db_constitution.updated_at = datetime.now(timezone.utc)
    
    db.add(db_constitution)
    db.commit()
    db.refresh(db_constitution)
    return db_constitution

def delete_constitution(db: Session, constitution_id: str) -> bool:
    """Delete an AI Constitution."""
    db_constitution = get_constitution(db, constitution_id)
    if not db_constitution:
        return False
    
    db.delete(db_constitution)
    db.commit()
    return True

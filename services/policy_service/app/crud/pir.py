from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
import json

from .. import models
# Import the common schemas - adjust the import path as needed
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from common.schemas import pir as schemas

# Import Kafka producer
from ..core.kafka_producer import send_policy_update_event

def get_policy(db: Session, policy_id: str) -> Optional[models.PIRModel]:
    return db.query(models.PIRModel).filter(models.PIRModel.id == policy_id).first()

def get_policies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    min_priority: Optional[int] = None,
    tags: Optional[List[str]] = None,
    constitutional_references: Optional[List[str]] = None,
    # New v2 filter parameters
    version_id: Optional[str] = None,
    formal_verification_status: Optional[str] = None,
    source_regulation: Optional[str] = None,
    jurisdiction: Optional[str] = None
) -> List[models.PIRModel]:
    """
    Get policies with optional filtering by various criteria including new v2 fields.
    """
    query = db.query(models.PIRModel)

    # Apply filters if provided
    if status:
        query = query.filter(models.PIRModel.status == status)

    if severity:
        query = query.filter(models.PIRModel.severity == severity)

    if min_priority is not None:
        query = query.filter(models.PIRModel.priority >= min_priority)

    if tags:
        # Filter by any of the provided tags
        query = query.filter(models.PIRModel.tags.contains(tags))

    if constitutional_references:
        # Filter by any of the provided constitutional references
        query = query.filter(models.PIRModel.constitutional_references.contains(constitutional_references))
        
    # New v2 filters
    if version_id:
        query = query.filter(models.PIRModel.version_id == version_id)
        
    if formal_verification_status:
        # Filter by formal verification status in metadata
        # This is a JSONB path query to check the status field within the formal_verification object
        query = query.filter(models.PIRModel.metadata_.contains({"formal_verification": {"status": formal_verification_status}}))
    
    if source_regulation:
        # Filter by source regulation reference
        # This is a more complex JSONB query to find a specific source ID in the array
        query = query.filter(models.PIRModel.source_regulation_references.contains([{"sourceId": source_regulation}]))
    
    if jurisdiction:
        # Filter by jurisdiction in source regulation references
        query = query.filter(models.PIRModel.source_regulation_references.contains([{"jurisdiction": jurisdiction}]))

    # Order by priority (highest first) and then by creation date (newest first)
    query = query.order_by(models.PIRModel.priority.desc(), models.PIRModel.created_at.desc())

    return query.offset(skip).limit(limit).all()

def create_policy(db: Session, policy: schemas.PIR) -> models.PIRModel:
    """Create a new policy in the database."""
    # Handle both legacy and new trigger_conditions format
    if isinstance(policy.trigger_conditions, list):
        trigger_conditions = [cond.dict() for cond in policy.trigger_conditions]
    else:
        trigger_conditions = policy.trigger_conditions.dict()

    # Handle both legacy and new metadata format
    if isinstance(policy.metadata, dict):
        metadata = policy.metadata
    else:
        metadata = policy.metadata.dict()

    # Create the base policy object
    db_policy = models.PIRModel(
        id=policy.policy_id,
        version=policy.version,
        name=policy.name,
        description=policy.description,
        status=policy.status,
        constitutional_references=policy.constitutional_references,
        scope=policy.scope.dict(),
        trigger_conditions=trigger_conditions,
        governance_actions=[action.dict() for action in policy.governance_actions],
        severity=policy.severity,
        priority=policy.priority,
        tags=policy.tags,
        created_by=policy.created_by,
        updated_by=policy.updated_by,
        metadata_=metadata
    )
    
    # Handle new v2 fields
    if hasattr(policy, 'version_id') and policy.version_id is not None:
        db_policy.version_id = policy.version_id
    else:
        # Generate a version_id if not provided
        db_policy.version_id = f"{policy.policy_id}_v{policy.version}.0.0"
        
    if hasattr(policy, 'source_regulation_references') and policy.source_regulation_references:
        if hasattr(policy.source_regulation_references, 'dict'):
            db_policy.source_regulation_references = policy.source_regulation_references.dict()
        else:
            db_policy.source_regulation_references = policy.source_regulation_references
            
    if hasattr(policy, 'temporal_logic_annotations') and policy.temporal_logic_annotations:
        db_policy.temporal_logic_annotations = policy.temporal_logic_annotations.dict() if hasattr(policy.temporal_logic_annotations, 'dict') else policy.temporal_logic_annotations
        
    if hasattr(policy, 'homomorphic_encryption_policy') and policy.homomorphic_encryption_policy:
        db_policy.homomorphic_encryption_policy = policy.homomorphic_encryption_policy.dict() if hasattr(policy.homomorphic_encryption_policy, 'dict') else policy.homomorphic_encryption_policy
        
    if hasattr(policy, 'quantum_optimization_hints') and policy.quantum_optimization_hints:
        db_policy.quantum_optimization_hints = policy.quantum_optimization_hints.dict() if hasattr(policy.quantum_optimization_hints, 'dict') else policy.quantum_optimization_hints
    
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    
    # Send Kafka event for policy creation
    send_policy_update_event(db_policy.to_dict(), "policy_created")
    
    return db_policy

def update_policy(
    db: Session,
    db_policy: models.PIRModel,
    policy_update: dict
) -> models.PIRModel:
    """Update an existing policy in the database."""
    update_data = policy_update.copy()

    for field, value in update_data.items():
        if field == "trigger_conditions":
            # Handle both legacy and new trigger_conditions format
            if isinstance(value, list):
                processed_value = [cond.dict() if hasattr(cond, 'dict') else cond for cond in value]
            else:
                processed_value = value.dict() if hasattr(value, 'dict') else value
            setattr(db_policy, field, processed_value)
        elif field == "governance_actions":
            setattr(db_policy, field, [action.dict() if hasattr(action, 'dict') else action for action in value])
        elif field == "scope":
            setattr(db_policy, field, value.dict() if hasattr(value, 'dict') else value)
        # Handle new v2 fields
        elif field == "source_regulation_references":
            db_policy.source_regulation_references = value.dict() if hasattr(value, 'dict') else value
        elif field == "temporal_logic_annotations":
            db_policy.temporal_logic_annotations = value.dict() if hasattr(value, 'dict') else value
        elif field == "homomorphic_encryption_policy":
            db_policy.homomorphic_encryption_policy = value.dict() if hasattr(value, 'dict') else value
        elif field == "quantum_optimization_hints":
            db_policy.quantum_optimization_hints = value.dict() if hasattr(value, 'dict') else value
        elif field != "metadata" and field != "metadata_":
            setattr(db_policy, field, value)

    # Handle metadata update
    if "metadata" in update_data:
        metadata_value = update_data["metadata"]
        db_policy.metadata_ = metadata_value.dict() if hasattr(metadata_value, 'dict') else metadata_value

    # Update version and timestamp
    db_policy.version += 1
    db_policy.updated_at = datetime.now(timezone.utc)
    
    # Update version_id if it's not explicitly provided in the update
    if "version_id" not in update_data:
        # Increment the minor version number in version_id
        if db_policy.version_id:
            parts = db_policy.version_id.split('_v')
            if len(parts) == 2:
                base_id = parts[0]
                version_parts = parts[1].split('.')
                if len(version_parts) >= 2:
                    # Increment minor version
                    version_parts[1] = str(int(version_parts[1]) + 1)
                    db_policy.version_id = f"{base_id}_v{'.'.join(version_parts)}"
        else:
            # Create a new version_id if it doesn't exist
            db_policy.version_id = f"{db_policy.id}_v{db_policy.version}.0.0"

    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    
    # Send Kafka event for policy update
    send_policy_update_event(db_policy.to_dict(), "policy_updated")
    
    return db_policy

def delete_policy(db: Session, policy_id: str) -> bool:
    db_policy = get_policy(db, policy_id)
    if not db_policy:
        return False
    
    # Store policy data before deletion for Kafka event
    policy_data = db_policy.to_dict()
    
    db.delete(db_policy)
    db.commit()
    
    # Send Kafka event for policy deletion
    send_policy_update_event(policy_data, "policy_deleted")
    
    return True

def get_policy_by_name_version(
    db: Session,
    name: str,
    version: Optional[int] = None
) -> Optional[models.PIRModel]:
    query = db.query(models.PIRModel).filter(models.PIRModel.name == name)

    if version is not None:
        query = query.filter(models.PIRModel.version == version)
    else:
        # Get the latest version if no version specified
        query = query.order_by(models.PIRModel.version.desc())

    return query.first()

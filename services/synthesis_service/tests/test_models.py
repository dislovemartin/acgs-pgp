import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.policy import PolicyModel
from app.schemas.pir import PIR

def test_policy_model(db_session: Session):
    """Test the PolicyModel database model."""
    # Create test data
    policy_data = {
        "id": "test-id",
        "version": 1,
        "name": "Test Policy",
        "description": "Test policy description",
        "status": "draft",
        "trigger_conditions": [
            {"condition_type": "prompt_pattern", "parameters": {"patterns": ["test"]}}
        ],
        "governance_actions": [
            {"action_type": "block_execution", "parameters": {"message": "Test"}, "priority": 100}
        ],
        "tags": ["test"],
        "metadata": {"test": "test"},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by": "test",
        "updated_by": "test"
    }
    
    # Create a PIR instance
    pir = PIR(**policy_data)
    
    # Create a PolicyModel instance from PIR
    policy = PolicyModel(**policy_data)
    
    # Add to session and commit
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    
    # Retrieve the policy from the database
    db_policy = db_session.query(PolicyModel).filter(PolicyModel.id == "test-id").first()
    
    # Assert the policy was saved correctly
    assert db_policy is not None
    assert db_policy.name == "Test Policy"
    assert db_policy.description == "Test policy description"
    assert db_policy.status == "draft"
    assert len(db_policy.trigger_conditions) == 1
    assert len(db_policy.governance_actions) == 1
    assert db_policy.tags == ["test"]
    assert db_policy.metadata_ == {"test": "test"}
    assert db_policy.created_by == "test"
    assert db_policy.updated_by == "test"

def test_policy_model_to_pir():
    """Test conversion from PolicyModel to PIR."""
    # Create test data
    policy_data = {
        "id": "test-id",
        "version": 1,
        "name": "Test Policy",
        "description": "Test policy description",
        "status": "draft",
        "trigger_conditions": [
            {"condition_type": "prompt_pattern", "parameters": {"patterns": ["test"]}}
        ],
        "governance_actions": [
            {"action_type": "block_execution", "parameters": {"message": "Test"}, "priority": 100}
        ],
        "tags": ["test"],
        "metadata_": {"test": "test"},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by": "test",
        "updated_by": "test"
    }
    
    # Create a PolicyModel instance
    policy = PolicyModel(**policy_data)
    
    # Convert to PIR
    pir = policy.to_pir()
    
    # Assert the conversion was successful
    assert isinstance(pir, PIR)
    assert pir.id == "test-id"
    assert pir.name == "Test Policy"
    assert len(pir.trigger_conditions) == 1
    assert len(pir.governance_actions) == 1

@pytest.mark.parametrize("status", ["draft", "active", "inactive", "archived"])
def test_policy_model_status_validation(status, db_session: Session):
    """Test validation of policy status values."""
    # Create a policy with the given status
    policy = PolicyModel(
        id=f"test-{status}",
        version=1,
        name=f"Test Policy {status}",
        description="Test policy description",
        status=status,
        trigger_conditions=[],
        governance_actions=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by="test",
        updated_by="test"
    )
    
    # Add to session and commit
    db_session.add(policy)
    db_session.commit()
    
    # Retrieve the policy from the database
    db_policy = db_session.query(PolicyModel).filter(PolicyModel.id == f"test-{status}").first()
    
    # Assert the status was saved correctly
    assert db_policy.status == status

def test_policy_model_invalid_status():
    """Test that an invalid status raises a validation error."""
    with pytest.raises(ValueError):
        PolicyModel(
            id="test-invalid",
            version=1,
            name="Test Policy Invalid",
            description="Test policy description",
            status="invalid",
            trigger_conditions=[],
            governance_actions=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by="test",
            updated_by="test"
        )

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta
from app.models.policy import PolicyModel
from app.db.session import Base, engine, get_db

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = Session(bind=engine)
    
    try:
        yield db
    finally:
        # Rollback any changes
        db.rollback()
        
        # Close the session
        db.close()
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)

def test_create_policy(db_session: Session):
    """Test creating a policy in the database."""
    # Create test data
    policy = PolicyModel(
        id="test-create",
        version=1,
        name="Test Create Policy",
        description="Test creating a policy",
        status="draft",
        trigger_conditions=[
            {"condition_type": "prompt_pattern", "parameters": {"patterns": ["test"]}}
        ],
        governance_actions=[
            {"action_type": "block_execution", "parameters": {"message": "Test"}, "priority": 100}
        ],
        tags=["test"],
        metadata_={"test": "test"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by="test",
        updated_by="test"
    )
    
    # Add to session and commit
    db_session.add(policy)
    db_session.commit()
    
    # Retrieve the policy
    db_policy = db_session.query(PolicyModel).filter(PolicyModel.id == "test-create").first()
    
    # Assert the policy was saved correctly
    assert db_policy is not None
    assert db_policy.name == "Test Create Policy"
    assert db_policy.status == "draft"

def test_update_policy(db_session: Session):
    """Test updating a policy in the database."""
    # Create a test policy
    policy = PolicyModel(
        id="test-update",
        version=1,
        name="Test Update Policy",
        description="Test updating a policy",
        status="draft",
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
    
    # Update the policy
    policy.name = "Updated Test Policy"
    policy.status = "active"
    policy.updated_at = datetime.now(timezone.utc)
    policy.updated_by = "test-update"
    
    # Commit the changes
    db_session.commit()
    
    # Retrieve the updated policy
    updated_policy = db_session.query(PolicyModel).filter(PolicyModel.id == "test-update").first()
    
    # Assert the policy was updated correctly
    assert updated_policy.name == "Updated Test Policy"
    assert updated_policy.status == "active"
    assert updated_policy.updated_by == "test-update"

def test_delete_policy(db_session: Session):
    """Test deleting a policy from the database."""
    # Create a test policy
    policy = PolicyModel(
        id="test-delete",
        version=1,
        name="Test Delete Policy",
        description="Test deleting a policy",
        status="draft",
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
    
    # Delete the policy
    db_session.delete(policy)
    db_session.commit()
    
    # Try to retrieve the deleted policy
    deleted_policy = db_session.query(PolicyModel).filter(PolicyModel.id == "test-delete").first()
    
    # Assert the policy was deleted
    assert deleted_policy is None

def test_policy_versioning(db_session: Session):
    """Test policy versioning in the database."""
    # Create a test policy
    policy = PolicyModel(
        id="test-version",
        version=1,
        name="Test Version Policy",
        description="Test policy versioning",
        status="draft",
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
    
    # Create a new version of the policy
    new_version = PolicyModel(
        id="test-version",
        version=2,
        name="Test Version Policy v2",
        description="Updated test policy versioning",
        status="active",
        trigger_conditions=[],
        governance_actions=[],
        created_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        updated_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        created_by="test",
        updated_by="test"
    )
    
    # Add the new version to the session and commit
    db_session.add(new_version)
    db_session.commit()
    
    # Retrieve both versions
    versions = db_session.query(PolicyModel).filter(PolicyModel.id == "test-version").order_by(PolicyModel.version).all()
    
    # Assert both versions exist
    assert len(versions) == 2
    assert versions[0].version == 1
    assert versions[1].version == 2
    assert versions[0].status == "draft"
    assert versions[1].status == "active"

def test_policy_unique_constraint(db_session: Session):
    """Test the unique constraint on policy ID and version."""
    # Create a test policy
    policy1 = PolicyModel(
        id="test-unique",
        version=1,
        name="Test Unique Policy",
        description="Test unique constraint",
        status="draft",
        trigger_conditions=[],
        governance_actions=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by="test",
        updated_by="test"
    )
    
    # Add to session and commit
    db_session.add(policy1)
    db_session.commit()
    
    # Try to create another policy with the same ID and version
    policy2 = PolicyModel(
        id="test-unique",
        version=1,  # Same ID and version as policy1
        name="Test Duplicate Policy",
        description="Test duplicate ID and version",
        status="draft",
        trigger_conditions=[],
        governance_actions=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by="test",
        updated_by="test"
    )
    
    # Add to session and expect an IntegrityError
    db_session.add(policy2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    # Rollback the failed transaction
    db_session.rollback()

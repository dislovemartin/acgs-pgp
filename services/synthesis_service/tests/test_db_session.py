import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.session import Base, get_db
from app.models.policy import PolicyModel
from datetime import datetime, timezone

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

def test_get_db():
    """Test the get_db dependency."""
    # Create a test engine and session
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Override the get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Get a database session
    db_gen = override_get_db()
    db = next(db_gen)
    
    # Verify the session works
    assert db is not None
    assert isinstance(db, Session)
    
    # Clean up
    try:
        next(db_gen)
    except StopIteration:
        pass

def test_database_operations():
    """Test basic database operations."""
    # Create a test engine and session
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        # Create a test policy
        policy = PolicyModel(
            id="test-id",
            version=1,
            name="Test Policy",
            description="Test policy description",
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
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
        # Retrieve the policy
        db_policy = db.query(PolicyModel).filter(PolicyModel.id == "test-id").first()
        
        # Assert the policy was saved correctly
        assert db_policy is not None
        assert db_policy.name == "Test Policy"
        assert db_policy.status == "draft"
        
    finally:
        # Clean up
        db.close()

def test_database_rollback():
    """Test that database transactions are properly rolled back on error."""
    # Create a test engine and session
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        # Create a test policy with an invalid status (should raise an error)
        with pytest.raises(ValueError):
            policy = PolicyModel(
                id="test-rollback",
                version=1,
                name="Test Rollback Policy",
                description="Test rollback policy description",
                status="invalid_status",  # This should cause a validation error
                trigger_conditions=[],
                governance_actions=[],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                created_by="test",
                updated_by="test"
            )
            
            # This should not be reached due to the validation error
            db.add(policy)
            db.commit()
            
        # The transaction should be rolled back
        db.rollback()
        
        # Verify no policies were saved
        count = db.query(PolicyModel).count()
        assert count == 0
        
    finally:
        # Clean up
        db.close()

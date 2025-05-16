import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import Base, get_db, SessionLocal
from app.models.policy import PolicyModel
from datetime import datetime, timezone

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Fixtures

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    # Create an in-memory SQLite database
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Override the get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Return the session maker and the override function
    return TestingSessionLocal, override_get_db

def test_get_db_session(test_db):
    """Test getting a database session."""
    TestingSessionLocal, override_get_db = test_db
    
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

@pytest.mark.asyncio
async def test_database_operations(test_db):
    """Test database operations within a session."""
    TestingSessionLocal, override_get_db = test_db
    
    # Get a database session
    db_gen = override_get_db()
    db = next(db_gen)
    
    try:
        # Create a test policy
        policy = PolicyModel(
            id="test-session",
            version=1,
            name="Test Session Policy",
            description="Test database session operations",
            status="draft",
            trigger_conditions=[
                {"condition_type": "prompt_pattern", "parameters": {"patterns": ["test"]}}
            ],
            governance_actions=[
                {"action_type": "block_execution", "parameters": {"message": "Test"}, "priority": 100}
            ],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by="test",
            updated_by="test"
        )
        
        # Add to session
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
        # Retrieve the policy
        db_policy = db.query(PolicyModel).filter(PolicyModel.id == "test-session").first()
        
        # Verify the policy was saved correctly
        assert db_policy is not None
        assert db_policy.name == "Test Session Policy"
        assert db_policy.status == "draft"
        
    finally:
        # Clean up
        try:
            next(db_gen)
        except StopIteration:
            pass

def test_session_rollback_on_error(test_db):
    """Test that the session is rolled back on error."""
    TestingSessionLocal, override_get_db = test_db
    
    # Get a database session
    db_gen = override_get_db()
    db = next(db_gen)
    
    try:
        # Create a test policy with an invalid status (should raise an error)
        with pytest.raises(ValueError):
            policy = PolicyModel(
                id="test-rollback",
                version=1,
                name="Test Rollback Policy",
                description="Test session rollback on error",
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
        try:
            next(db_gen)
        except StopIteration:
            pass

def test_session_close_on_exception(test_db):
    """Test that the session is properly closed when an exception occurs."""
    TestingSessionLocal, override_get_db = test_db
    
    # Get a database session
    db_gen = override_get_db()
    db = next(db_gen)
    
    # Verify the session is open
    assert not db.invalidated
    
    # Simulate an exception
    try:
        raise Exception("Test exception")
    except Exception:
        # The session should be closed by the finally block in override_get_db
        pass
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass
    
    # The session should be closed now
    assert db.invalidated

def test_session_local_scope():
    """Test that each request gets its own database session."""
    # Create a test database
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autoclear=False, autocommit=False, bind=engine)
    
    # Create the first session
    db1 = TestingSessionLocal()
    
    # Create the second session
    db2 = TestingSessionLocal()
    
    # Verify they are different objects
    assert db1 is not db2
    
    # Clean up
    db1.close()
    db2.close()

def test_session_commit_rollback(test_db):
    """Test commit and rollback operations."""
    TestingSessionLocal, override_get_db = test_db
    
    # Get a database session
    db_gen = override_get_db()
    db = next(db_gen)
    
    try:
        # Create a test policy
        policy = PolicyModel(
            id="test-commit",
            version=1,
            name="Test Commit Policy",
            description="Test commit and rollback",
            status="draft",
            trigger_conditions=[],
            governance_actions=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by="test",
            updated_by="test"
        )
        
        # Add to session but don't commit yet
        db.add(policy)
        
        # The policy should not be in the database yet
        db_policy = db.query(PolicyModel).filter(PolicyModel.id == "test-commit").first()
        assert db_policy is None  # Not committed yet
        
        # Commit the transaction
        db.commit()
        
        # Now the policy should be in the database
        db_policy = db.query(PolicyModel).filter(PolicyModel.id == "test-commit").first()
        assert db_policy is not None
        
        # Rollback the transaction
        db.rollback()
        
        # The policy should still be in the database (rollback doesn't undo committed changes)
        db_policy = db.query(PolicyModel).filter(PolicyModel.id == "test-commit").first()
        assert db_policy is not None
        
    finally:
        # Clean up
        try:
            next(db_gen)
        except StopIteration:
            pass

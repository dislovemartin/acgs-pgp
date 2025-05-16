import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
import sys
import os

# Add the parent directory to the path so we can import the common schemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from common.schemas.constitution import (
    AIConstitution, AIConstitutionBase, AIConstitutionCreate, AIConstitutionUpdate,
    AIConstitutionPrinciple
)

# Test data
TEST_TIMESTAMP = datetime.now(timezone.utc)

class TestAIConstitutionPrinciple:
    """Test suite for AIConstitutionPrinciple model."""
    
    def test_valid_principle(self):
        """Test valid principle creation."""
        principle = AIConstitutionPrinciple(
            article_id="privacy.1",
            title="Privacy Protection",
            description="AI systems must respect and protect user privacy.",
            category="privacy",
            keywords=["privacy", "data protection", "confidentiality"],
            examples=[
                "Avoid collecting unnecessary personal data",
                "Implement strong data protection measures"
            ],
            related_articles=["security.1", "transparency.2"],
            metadata={
                "source": "GDPR",
                "importance": "critical"
            }
        )
        
        assert principle.article_id == "privacy.1"
        assert principle.title == "Privacy Protection"
        assert principle.description == "AI systems must respect and protect user privacy."
        assert principle.category == "privacy"
        assert principle.keywords == ["privacy", "data protection", "confidentiality"]
        assert len(principle.examples) == 2
        assert principle.related_articles == ["security.1", "transparency.2"]
        assert principle.metadata == {"source": "GDPR", "importance": "critical"}
    
    def test_principle_with_defaults(self):
        """Test principle with default values."""
        principle = AIConstitutionPrinciple(
            title="Minimal Principle",
            description="A minimal principle"
        )
        
        assert principle.article_id is not None  # UUID is generated
        assert principle.title == "Minimal Principle"
        assert principle.description == "A minimal principle"
        assert principle.category is None
        assert principle.keywords == []
        assert principle.examples == []
        assert principle.related_articles == []
        assert principle.metadata == {}
    
    def test_invalid_principle(self):
        """Test invalid principle creation."""
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            AIConstitutionPrinciple(title="Missing Description")
        assert any("field required" in str(err) for err in exc_info.value.errors())
        
        with pytest.raises(ValidationError) as exc_info:
            AIConstitutionPrinciple(description="Missing Title")
        assert any("field required" in str(err) for err in exc_info.value.errors())

class TestAIConstitution:
    """Test suite for AIConstitution model."""
    
    @pytest.fixture
    def valid_constitution_data(self):
        """Fixture providing valid AIConstitution data for testing."""
        return {
            "title": "AI Constitution for Responsible AI",
            "description": "Foundational principles for responsible AI governance",
            "principles": [
                AIConstitutionPrinciple(
                    article_id="privacy.1",
                    title="Privacy Protection",
                    description="AI systems must respect and protect user privacy.",
                    category="privacy",
                    keywords=["privacy", "data protection"],
                    examples=["Example 1", "Example 2"],
                    related_articles=["security.1"]
                ),
                AIConstitutionPrinciple(
                    article_id="fairness.1",
                    title="Fairness and Non-discrimination",
                    description="AI systems must be designed to avoid unfair bias and discrimination.",
                    category="fairness",
                    keywords=["fairness", "bias", "discrimination"],
                    examples=["Example 1", "Example 2"],
                    related_articles=["transparency.1"]
                )
            ],
            "categories": ["privacy", "fairness", "transparency", "security"],
            "metadata": {
                "version_notes": "Initial version",
                "approved_by": "ethics_board",
                "approval_date": TEST_TIMESTAMP.isoformat()
            }
        }
    
    def test_valid_constitution_creation(self, valid_constitution_data):
        """Test valid AIConstitution creation."""
        constitution = AIConstitution(
            id="test-id",
            version=1,
            created_at=TEST_TIMESTAMP,
            updated_at=TEST_TIMESTAMP,
            created_by="test-user",
            updated_by="test-user",
            **valid_constitution_data
        )
        
        assert constitution.id == "test-id"
        assert constitution.version == 1
        assert constitution.title == "AI Constitution for Responsible AI"
        assert constitution.description == "Foundational principles for responsible AI governance"
        assert len(constitution.principles) == 2
        assert constitution.categories == ["privacy", "fairness", "transparency", "security"]
        assert constitution.created_at == TEST_TIMESTAMP
        assert constitution.updated_at == TEST_TIMESTAMP
        assert constitution.created_by == "test-user"
        assert constitution.updated_by == "test-user"
        assert constitution.metadata["version_notes"] == "Initial version"
    
    def test_constitution_create_and_update(self, valid_constitution_data):
        """Test AIConstitutionCreate and AIConstitutionUpdate models."""
        # Test AIConstitutionCreate
        create_data = valid_constitution_data.copy()
        create_data["created_by"] = "creator"
        create_data["updated_by"] = "creator"
        
        constitution_create = AIConstitutionCreate(**create_data)
        assert constitution_create.title == "AI Constitution for Responsible AI"
        assert constitution_create.version == 1
        assert constitution_create.created_by == "creator"
        assert constitution_create.updated_by == "creator"
        
        # Test AIConstitutionUpdate
        update_data = {
            "title": "Updated AI Constitution",
            "description": "Updated description",
            "updated_by": "updater"
        }
        constitution_update = AIConstitutionUpdate(**update_data)
        assert constitution_update.title == "Updated AI Constitution"
        assert constitution_update.description == "Updated description"
        assert constitution_update.updated_by == "updater"
        assert constitution_update.principles is None  # Not updated
    
    def test_constitution_with_defaults(self):
        """Test AIConstitution with default values."""
        constitution = AIConstitutionBase(
            title="Minimal Constitution",
            description="A minimal constitution"
        )
        
        assert constitution.title == "Minimal Constitution"
        assert constitution.description == "A minimal constitution"
        assert constitution.principles == []
        assert constitution.categories == []
        assert constitution.metadata == {}
    
    def test_invalid_constitution(self):
        """Test invalid AIConstitution creation."""
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            AIConstitutionBase(title="Missing Description")
        assert any("field required" in str(err) for err in exc_info.value.errors())
        
        with pytest.raises(ValidationError) as exc_info:
            AIConstitutionBase(description="Missing Title")
        assert any("field required" in str(err) for err in exc_info.value.errors())
        
        # Test invalid principles type
        with pytest.raises(ValidationError) as exc_info:
            AIConstitutionBase(
                title="Invalid Principles",
                description="Test",
                principles="not-a-list"
            )
        assert any("value is not a valid list" in str(err) for err in exc_info.value.errors())
        
        # Test invalid categories type
        with pytest.raises(ValidationError) as exc_info:
            AIConstitutionBase(
                title="Invalid Categories",
                description="Test",
                categories="not-a-list"
            )
        assert any("value is not a valid list" in str(err) for err in exc_info.value.errors())
        
        # Test invalid metadata type
        with pytest.raises(ValidationError) as exc_info:
            AIConstitutionBase(
                title="Invalid Metadata",
                description="Test",
                metadata="not-a-dict"
            )
        assert any("value is not a valid dict" in str(err) for err in exc_info.value.errors())

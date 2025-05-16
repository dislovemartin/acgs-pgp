from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

class AIConstitutionPrinciple(BaseModel):
    """A principle in the AI Constitution."""
    article_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    related_articles: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AIConstitutionBase(BaseModel):
    """Base class for AI Constitution schemas."""
    title: str
    description: str
    principles: List[AIConstitutionPrinciple] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AIConstitutionCreate(AIConstitutionBase):
    """Schema for creating a new AI Constitution."""
    version: int = 1
    created_by: str = "system"
    updated_by: str = "system"

class AIConstitutionUpdate(BaseModel):
    """Schema for updating an existing AI Constitution."""
    title: Optional[str] = None
    description: Optional[str] = None
    principles: Optional[List[AIConstitutionPrinciple]] = None
    categories: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_by: Optional[str] = None

class AIConstitution(AIConstitutionBase):
    """AI Constitution schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    updated_by: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "version": 1,
                "title": "AI Constitution for Responsible AI",
                "description": "Foundational principles for responsible AI governance",
                "principles": [
                    {
                        "article_id": "privacy.1",
                        "title": "Privacy Protection",
                        "description": "AI systems must respect and protect user privacy.",
                        "category": "privacy",
                        "keywords": ["privacy", "data protection", "confidentiality"],
                        "examples": [
                            "Avoid collecting unnecessary personal data",
                            "Implement strong data protection measures"
                        ],
                        "related_articles": ["security.1", "transparency.2"],
                        "metadata": {
                            "source": "GDPR",
                            "importance": "critical"
                        }
                    },
                    {
                        "article_id": "fairness.1",
                        "title": "Fairness and Non-discrimination",
                        "description": "AI systems must be designed to avoid unfair bias and discrimination.",
                        "category": "fairness",
                        "keywords": ["fairness", "bias", "discrimination", "equity"],
                        "examples": [
                            "Test for bias in training data",
                            "Implement fairness metrics in model evaluation"
                        ],
                        "related_articles": ["transparency.1", "accountability.2"],
                        "metadata": {
                            "source": "IEEE Ethics Guidelines",
                            "importance": "critical"
                        }
                    }
                ],
                "categories": ["privacy", "fairness", "transparency", "security", "accountability"],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "created_by": "system@acgs-pgp.local",
                "updated_by": "system@acgs-pgp.local",
                "metadata": {
                    "version_notes": "Initial version",
                    "approved_by": "ethics_board",
                    "approval_date": "2023-01-01T00:00:00Z"
                }
            }
        }

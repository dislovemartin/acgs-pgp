from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class AIConstitutionModel(Base):
    """Database model for the AI Constitution."""
    __tablename__ = "ai_constitution"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    version = Column(Integer, default=1, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    principles = Column(JSONB, nullable=False, default=list)
    categories = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False)
    metadata_ = Column("metadata", JSONB, default=dict)
    
    def to_dict(self):
        """Convert the model to a dictionary that matches the AIConstitution schema."""
        return {
            "id": self.id,
            "version": self.version,
            "title": self.title,
            "description": self.description,
            "principles": self.principles,
            "categories": self.categories,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "metadata": self.metadata_
        }

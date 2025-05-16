from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
import uuid

from ..db.session import Base

# Helper function for timezone-aware UTC timestamps
def utc_now():
    return datetime.now(timezone.utc)

class PolicyModel(Base):
    """
    Database model for storing synthesized policies.
    """
    __tablename__ = "synthesized_policies"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    policy_id = Column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    description = Column(String(1000), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    version = Column(Integer, default=1, nullable=False)

    # Policy definition
    constitutional_references = Column(JSONB, default=list)
    scope = Column(JSONB, default=dict)
    trigger_conditions = Column(JSONB, nullable=False)
    governance_actions = Column(JSONB, nullable=False)
    severity = Column(String(50), default="medium")
    priority = Column(Integer, default=50)

    # Metadata
    metadata_ = Column("metadata", JSONB, default=dict)

    # Audit fields
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "policy_id": self.policy_id,
            "description": self.description,
            "status": self.status,
            "version": self.version,
            "constitutional_references": self.constitutional_references,
            "scope": self.scope,
            "trigger_conditions": self.trigger_conditions,
            "governance_actions": self.governance_actions,
            "severity": self.severity,
            "priority": self.priority,
            "metadata": self.metadata_,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

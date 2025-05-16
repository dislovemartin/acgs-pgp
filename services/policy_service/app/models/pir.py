from sqlalchemy import Column, String, Integer, Enum, JSON, DateTime, func, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class PIRModel(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    version = Column(Integer, default=1, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="DRAFT")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False)

    # Base P-IR schema fields
    constitutional_references = Column(JSONB, default=list)
    scope = Column(JSONB, default=dict)
    trigger_conditions = Column(JSONB, nullable=False)
    governance_actions = Column(JSONB, nullable=False)
    severity = Column(String(50), default="MEDIUM")
    priority = Column(Integer, default=50)
    tags = Column(JSONB, default=list)
    metadata_ = Column("metadata", JSONB, default=dict)
    
    # New v2 fields
    version_id = Column(String(255), nullable=True)  # e.g., pirId_vX.Y.Z
    source_regulation_references = Column(JSONB, default=list)  # [{"sourceId": "GDPR Art. 5", "jurisdiction": "EU"}]
    temporal_logic_annotations = Column(JSONB, default=dict)  # TemporalLogicAnnotations
    homomorphic_encryption_policy = Column(JSONB, default=dict)  # HomomorphicEncryptionPolicy
    quantum_optimization_hints = Column(JSONB, default=dict)  # QuantumOptimizationHints

    def to_dict(self):
        """Convert the model to a dictionary that matches the PIR schema."""
        result = {
            "policy_id": self.id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "constitutional_references": self.constitutional_references,
            "scope": self.scope,
            "trigger_conditions": self.trigger_conditions,
            "governance_actions": self.governance_actions,
            "severity": self.severity,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "tags": self.tags,
            "metadata": self.metadata_
        }
        
        # Add new v2 fields if they have values
        if self.version_id:
            result["version_id"] = self.version_id
        if self.source_regulation_references:
            result["source_regulation_references"] = self.source_regulation_references
        if self.temporal_logic_annotations:
            result["temporal_logic_annotations"] = self.temporal_logic_annotations
        if self.homomorphic_encryption_policy:
            result["homomorphic_encryption_policy"] = self.homomorphic_encryption_policy
        if self.quantum_optimization_hints:
            result["quantum_optimization_hints"] = self.quantum_optimization_hints
            
        return result

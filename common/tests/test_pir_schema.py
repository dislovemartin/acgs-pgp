import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
import sys
import os

# Add the parent directory to the path so we can import the common schemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from common.schemas.pir import (
    PIR, PIRBase, PIRCreate, PIRUpdate,
    TriggerCondition, GovernanceAction, 
    TriggerConditions, PromptPattern, ContextAttribute, 
    ToolUsageRequest, ResponsePattern,
    Scope, PolicyStatus, PolicySeverity,
    TriggerConditionType, GovernanceActionType,
    ScopeModelInclusionType, ScopeUserRoleInclusionType,
    ScopeApplicationInclusionType, ScopeDataSensitivityInclusionType,
    ApprovalMetadata, SynthesisMetadata, PIRMetadata,
    # New v2 schema components
    PromptPatternMatcher, AnomalyScoreMatcher,
    LTLSpecification, TemporalLogicAnnotations,
    HomomorphicEncryptionPolicy, QuantumOptimizationHints,
    PQCSignature, FormalVerificationStatus
)

# Test data
TEST_TIMESTAMP = datetime.now(timezone.utc)

class TestScope:
    """Test suite for Scope model."""
    
    def test_valid_scope(self):
        """Test valid scope creation."""
        scope = Scope(
            llm_models_inclusion=ScopeModelInclusionType.INCLUDE,
            llm_models_list=["gpt-4", "claude-3"],
            user_roles_inclusion=ScopeUserRoleInclusionType.ALL,
            user_roles_list=[],
            applications_inclusion=ScopeApplicationInclusionType.EXCLUDE,
            applications_list=["app1"],
            data_sensitivity_inclusion=ScopeDataSensitivityInclusionType.MINIMUM,
            data_sensitivity_levels=["public", "internal", "confidential"],
            custom_scope_attributes={"region": "north-america"}
        )
        
        assert scope.llm_models_inclusion == ScopeModelInclusionType.INCLUDE
        assert scope.llm_models_list == ["gpt-4", "claude-3"]
        assert scope.user_roles_inclusion == ScopeUserRoleInclusionType.ALL
        assert scope.user_roles_list == []
        assert scope.applications_inclusion == ScopeApplicationInclusionType.EXCLUDE
        assert scope.applications_list == ["app1"]
        assert scope.data_sensitivity_inclusion == ScopeDataSensitivityInclusionType.MINIMUM
        assert scope.data_sensitivity_levels == ["public", "internal", "confidential"]
        assert scope.custom_scope_attributes == {"region": "north-america"}
    
    def test_scope_with_defaults(self):
        """Test scope with default values."""
        scope = Scope()
        
        assert scope.llm_models_inclusion == ScopeModelInclusionType.ALL
        assert scope.llm_models_list == []
        assert scope.user_roles_inclusion == ScopeUserRoleInclusionType.ALL
        assert scope.user_roles_list == []
        assert scope.applications_inclusion == ScopeApplicationInclusionType.ALL
        assert scope.applications_list == []
        assert scope.data_sensitivity_inclusion == ScopeDataSensitivityInclusionType.ALL
        assert scope.data_sensitivity_levels == []
        assert scope.custom_scope_attributes == {}

class TestTriggerConditions:
    """Test suite for TriggerConditions model."""
    
    def test_valid_trigger_conditions(self):
        """Test valid trigger conditions creation."""
        conditions = TriggerConditions(
            prompt_patterns=[
                PromptPattern(
                    pattern="test pattern",
                    is_regex=False,
                    case_sensitive=False,
                    description="Test pattern"
                ),
                PromptPattern(
                    pattern=r"\d{3}-\d{2}-\d{4}",
                    is_regex=True,
                    case_sensitive=False,
                    description="SSN pattern"
                )
            ],
            context_attributes=[
                ContextAttribute(
                    attribute_name="user_role",
                    attribute_value="admin",
                    match_type="exact",
                    description="Admin user"
                )
            ],
            tool_usage_requests=[
                ToolUsageRequest(
                    tool_name="sensitive_data_tool",
                    parameter_constraints={"access_level": "high"},
                    description="Sensitive data tool usage"
                )
            ],
            response_patterns=[
                ResponsePattern(
                    pattern="confidential",
                    is_regex=False,
                    case_sensitive=False,
                    description="Confidential information in response"
                )
            ],
            condition_logic="ANY"
        )
        
        assert len(conditions.prompt_patterns) == 2
        assert len(conditions.context_attributes) == 1
        assert len(conditions.tool_usage_requests) == 1
        assert len(conditions.response_patterns) == 1
        assert conditions.condition_logic == "ANY"
        assert conditions.custom_logic_expression is None
    
    def test_trigger_conditions_with_defaults(self):
        """Test trigger conditions with default values."""
        conditions = TriggerConditions()
        
        assert conditions.prompt_patterns == []
        assert conditions.context_attributes == []
        assert conditions.tool_usage_requests == []
        assert conditions.response_patterns == []
        assert conditions.custom_conditions == []
        assert conditions.condition_logic == "ANY"
        assert conditions.custom_logic_expression is None
    
    def test_custom_logic_expression(self):
        """Test trigger conditions with custom logic expression."""
        conditions = TriggerConditions(
            prompt_patterns=[
                PromptPattern(pattern="pattern1"),
                PromptPattern(pattern="pattern2")
            ],
            context_attributes=[
                ContextAttribute(attribute_name="attr1", attribute_value="value1")
            ],
            condition_logic="CUSTOM",
            custom_logic_expression="(prompt_patterns[0] OR prompt_patterns[1]) AND context_attributes[0]"
        )
        
        assert conditions.condition_logic == "CUSTOM"
        assert conditions.custom_logic_expression == "(prompt_patterns[0] OR prompt_patterns[1]) AND context_attributes[0]"

class TestEnhancedTriggerComponents:
    """Test suite for enhanced trigger components."""
    
    def test_prompt_pattern_matcher(self):
        """Test PromptPatternMatcher creation."""
        # Test with regex pattern
        matcher = PromptPatternMatcher(
            pattern_type="REGEX",
            value=r"\d{3}-\d{2}-\d{4}",
            case_sensitive=False,
            description="SSN pattern"
        )
        assert matcher.pattern_type == "REGEX"
        assert matcher.value == r"\d{3}-\d{2}-\d{4}"
        assert matcher.case_sensitive is False
        assert matcher.similarity_threshold is None
        assert matcher.embedding_model_id is None
        
        # Test with semantic similarity
        matcher = PromptPatternMatcher(
            pattern_type="SEMANTIC_SIMILARITY",
            value="sensitive personal information",
            similarity_threshold=0.85,
            embedding_model_id="text-embedding-ada-002",
            description="Semantic PII detection"
        )
        assert matcher.pattern_type == "SEMANTIC_SIMILARITY"
        assert matcher.value == "sensitive personal information"
        assert matcher.similarity_threshold == 0.85
        assert matcher.embedding_model_id == "text-embedding-ada-002"
        
        # Test with keyword list
        matcher = PromptPatternMatcher(
            pattern_type="KEYWORD_LIST",
            value=["ssn", "social security", "tax id"],
            case_sensitive=False
        )
        assert matcher.pattern_type == "KEYWORD_LIST"
        assert isinstance(matcher.value, list)
        assert len(matcher.value) == 3
    
    def test_anomaly_score_matcher(self):
        """Test AnomalyScoreMatcher creation."""
        matcher = AnomalyScoreMatcher(
            source="INFERENCE_GATEWAY_ISOLATION_FOREST",
            score_operator="GT",
            threshold=0.75,
            description="Anomaly detection for unusual prompts"
        )
        assert matcher.source == "INFERENCE_GATEWAY_ISOLATION_FOREST"
        assert matcher.score_operator == "GT"
        assert matcher.threshold == 0.75
        assert matcher.description == "Anomaly detection for unusual prompts"


class TestFormalVerificationComponents:
    """Test suite for formal verification components."""
    
    def test_ltl_specification(self):
        """Test LTLSpecification creation."""
        ltl_spec = LTLSpecification(
            property_id="safety-prop-001",
            formula="G (input_is_harmful -> !output_is_generated)",
            description="Safety property: harmful inputs never generate outputs",
            variables_mapping={
                "input_is_harmful": "$.trigger_conditions.prompt_patterns[0].pattern",
                "output_is_generated": "$.governance_actions[0].parameters.allow_output"
            }
        )
        assert ltl_spec.property_id == "safety-prop-001"
        assert ltl_spec.formula == "G (input_is_harmful -> !output_is_generated)"
        assert "Safety property" in ltl_spec.description
        assert len(ltl_spec.variables_mapping) == 2
    
    def test_temporal_logic_annotations(self):
        """Test TemporalLogicAnnotations creation."""
        annotations = TemporalLogicAnnotations(
            ltl_specifications=[
                LTLSpecification(
                    property_id="safety-prop-001",
                    formula="G (input_is_harmful -> !output_is_generated)"
                ),
                LTLSpecification(
                    property_id="liveness-prop-001",
                    formula="F (request_approval -> X approval_received)"
                )
            ]
        )
        assert len(annotations.ltl_specifications) == 2
        assert annotations.ltl_specifications[0].property_id == "safety-prop-001"
        assert annotations.ltl_specifications[1].property_id == "liveness-prop-001"


class TestCryptographyComponents:
    """Test suite for cryptography-related components."""
    
    def test_homomorphic_encryption_policy(self):
        """Test HomomorphicEncryptionPolicy creation."""
        policy = HomomorphicEncryptionPolicy(
            fields_to_encrypt=[
                "$.trigger_conditions.prompt_patterns[*].pattern",
                "$.metadata.custom_metadata.sensitive_field"
            ],
            he_scheme_id="BFV-128",
            key_management_policy_id="key-policy-001"
        )
        assert len(policy.fields_to_encrypt) == 2
        assert policy.he_scheme_id == "BFV-128"
        assert policy.key_management_policy_id == "key-policy-001"
    
    def test_pqc_signature(self):
        """Test PQCSignature creation."""
        signature = PQCSignature(
            algorithm="CRYSTALS-Dilithium2",
            signature_value="base64encodedvalue...",
            public_key_id="key_id_123"
        )
        assert signature.algorithm == "CRYSTALS-Dilithium2"
        assert signature.signature_value == "base64encodedvalue..."
        assert signature.public_key_id == "key_id_123"


class TestQuantumComponents:
    """Test suite for quantum-related components."""
    
    def test_quantum_optimization_hints(self):
        """Test QuantumOptimizationHints creation."""
        hints = QuantumOptimizationHints(
            qubo_formulation_hint="policy_evaluation_latency_optimization",
            target_objective="minimize_false_negatives"
        )
        assert hints.qubo_formulation_hint == "policy_evaluation_latency_optimization"
        assert hints.target_objective == "minimize_false_negatives"


class TestPIRMetadata:
    """Test suite for PIRMetadata model."""
    
    def test_valid_pir_metadata(self):
        """Test valid PIR metadata creation."""
        metadata = PIRMetadata(
            author="compliance-team",
            created_timestamp=TEST_TIMESTAMP,
            last_updated_timestamp=TEST_TIMESTAMP,
            approval_history=[
                ApprovalMetadata(
                    approved_by="compliance-officer",
                    approved_at=TEST_TIMESTAMP,
                    comments="Approved after review"
                )
            ],
            synthesis_details=SynthesisMetadata(
                synthesized_by="gpt-4",
                synthesized_at=TEST_TIMESTAMP,
                source_type="llm",
                source_details={"prompt": "Create a policy to prevent PII disclosure"},
                confidence_score=0.95
            ),
            compliance_standards=["GDPR", "CCPA"],
            custom_metadata={"business_unit": "customer_service"},
            # New v2 fields
            pqc_signature=PQCSignature(
                algorithm="CRYSTALS-Dilithium2",
                signature_value="base64encodedvalue...",
                public_key_id="key_id_123"
            ),
            formal_verification=FormalVerificationStatus(
                last_run_id="fv-run-123",
                status="VERIFIED",
                verified_timestamp_utc=TEST_TIMESTAMP,
                verified_properties=["safety-prop-001"]
            )
        )
        
        assert metadata.author == "compliance-team"
        assert metadata.created_timestamp == TEST_TIMESTAMP
        assert metadata.last_updated_timestamp == TEST_TIMESTAMP
        assert len(metadata.approval_history) == 1
        assert metadata.approval_history[0].approved_by == "compliance-officer"
        assert metadata.synthesis_details.synthesized_by == "gpt-4"
        assert metadata.synthesis_details.confidence_score == 0.95
        assert metadata.compliance_standards == ["GDPR", "CCPA"]
        assert metadata.custom_metadata == {"business_unit": "customer_service"}
        # Test new v2 fields
        assert metadata.pqc_signature.algorithm == "CRYSTALS-Dilithium2"
        assert metadata.formal_verification.status == "VERIFIED"
        assert len(metadata.formal_verification.verified_properties) == 1
    
    def test_pir_metadata_with_defaults(self):
        """Test PIR metadata with default values."""
        metadata = PIRMetadata()
        
        assert metadata.author is None
        assert metadata.created_timestamp is None
        assert metadata.last_updated_timestamp is None
        assert metadata.approval_history == []
        assert metadata.synthesis_details is None
        assert metadata.compliance_standards == []
        assert metadata.custom_metadata == {}
        # Test new v2 fields defaults
        assert metadata.pqc_signature is None
        assert metadata.formal_verification is None

class TestPIR:
    """Test suite for PIR model."""
    
    @pytest.fixture
    def valid_pir_data(self):
        """Fixture providing valid PIR data for testing."""
        return {
            "name": "Test Policy",
            "description": "Test policy description",
            "status": PolicyStatus.DRAFT,
            "constitutional_references": ["privacy.1", "security.3"],
            "scope": Scope(
                llm_models_inclusion=ScopeModelInclusionType.ALL,
                data_sensitivity_inclusion=ScopeDataSensitivityInclusionType.MINIMUM,
                data_sensitivity_levels=["public", "internal", "confidential"]
            ),
            "trigger_conditions": TriggerConditions(
                prompt_patterns=[
                    PromptPattern(pattern="test pattern")
                ],
                condition_logic="ANY",
                # New v2 fields
                operator="AND",
                conditions=[
                    PromptPatternMatcher(
                        pattern_type="REGEX",
                        value=r"\d{3}-\d{2}-\d{4}",
                        description="SSN pattern"
                    ),
                    AnomalyScoreMatcher(
                        source="INFERENCE_GATEWAY_ISOLATION_FOREST",
                        score_operator="GT",
                        threshold=0.75
                    )
                ]
            ),
            "governance_actions": [
                GovernanceAction(
                    action_type=GovernanceActionType.BLOCK_EXECUTION,
                    parameters={"message": "Test message"},
                    priority=100,
                    execution_order=1
                )
            ],
            "severity": PolicySeverity.HIGH,
            "priority": 80,
            "tags": ["test", "security"],
            "created_by": "test-user",
            "updated_by": "test-user",
            "metadata": PIRMetadata(
                author="compliance-team",
                compliance_standards=["GDPR"],
                pqc_signature=PQCSignature(
                    algorithm="CRYSTALS-Dilithium2",
                    signature_value="base64encodedvalue..."
                ),
                formal_verification=FormalVerificationStatus(
                    status="VERIFIED",
                    verified_properties=["safety-prop-001"]
                )
            ),
            # New v2 fields
            "version_id": "test-policy-v1.0.0",
            "source_regulation_references": [{"sourceId": "GDPR Art. 5", "jurisdiction": "EU"}],
            "temporal_logic_annotations": TemporalLogicAnnotations(
                ltl_specifications=[
                    LTLSpecification(
                        property_id="safety-prop-001",
                        formula="G (input_is_harmful -> !output_is_generated)"
                    )
                ]
            ),
            "homomorphic_encryption_policy": HomomorphicEncryptionPolicy(
                fields_to_encrypt=["$.trigger_conditions.prompt_patterns[*].pattern"],
                he_scheme_id="BFV-128"
            ),
            "quantum_optimization_hints": QuantumOptimizationHints(
                qubo_formulation_hint="policy_evaluation_latency_optimization"
            )
        }
    
    def test_valid_pir_creation(self, valid_pir_data):
        """Test valid PIR creation."""
        pir = PIR(**valid_pir_data)
        
        assert pir.name == "Test Policy"
        assert pir.description == "Test policy description"
        assert pir.status == PolicyStatus.DRAFT
        assert pir.constitutional_references == ["privacy.1", "security.3"]
        assert pir.scope.data_sensitivity_inclusion == ScopeDataSensitivityInclusionType.MINIMUM
        assert isinstance(pir.trigger_conditions, TriggerConditions)
        assert len(pir.governance_actions) == 1
        assert pir.severity == PolicySeverity.HIGH
        assert pir.priority == 80
        assert pir.tags == ["test", "security"]
        assert pir.created_by == "test-user"
        assert pir.updated_by == "test-user"
        assert isinstance(pir.metadata, PIRMetadata)
        assert pir.metadata.compliance_standards == ["GDPR"]
        
        # Test new v2 fields
        assert pir.version_id == "test-policy-v1.0.0"
        assert len(pir.source_regulation_references) == 1
        assert pir.source_regulation_references[0]["sourceId"] == "GDPR Art. 5"
        assert pir.source_regulation_references[0]["jurisdiction"] == "EU"
        assert isinstance(pir.temporal_logic_annotations, TemporalLogicAnnotations)
        assert len(pir.temporal_logic_annotations.ltl_specifications) == 1
        assert pir.homomorphic_encryption_policy.he_scheme_id == "BFV-128"
        assert pir.quantum_optimization_hints.qubo_formulation_hint == "policy_evaluation_latency_optimization"
        assert pir.metadata.pqc_signature.algorithm == "CRYSTALS-Dilithium2"
        assert pir.metadata.formal_verification.status == "VERIFIED"
    
    def test_pir_with_legacy_trigger_conditions(self, valid_pir_data):
        """Test PIR with legacy trigger conditions."""
        data = valid_pir_data.copy()
        data["trigger_conditions"] = [
            TriggerCondition(
                condition_type=TriggerConditionType.PROMPT_PATTERN,
                parameters={"patterns": ["test"]},
                description="Test condition"
            )
        ]
        
        pir = PIR(**data)
        
        assert isinstance(pir.trigger_conditions, list)
        assert len(pir.trigger_conditions) == 1
        assert pir.trigger_conditions[0].condition_type == TriggerConditionType.PROMPT_PATTERN
    
    def test_enhanced_trigger_conditions(self, valid_pir_data):
        """Test enhanced trigger conditions in PIR v2."""
        pir = PIR(**valid_pir_data)
        
        # Test the enhanced trigger conditions
        assert pir.trigger_conditions.operator == "AND"
        assert len(pir.trigger_conditions.conditions) == 2
        
        # Test PromptPatternMatcher in conditions
        prompt_matcher = pir.trigger_conditions.conditions[0]
        assert isinstance(prompt_matcher, PromptPatternMatcher)
        assert prompt_matcher.pattern_type == "REGEX"
        assert prompt_matcher.value == r"\d{3}-\d{2}-\d{4}"
        
        # Test AnomalyScoreMatcher in conditions
        anomaly_matcher = pir.trigger_conditions.conditions[1]
        assert isinstance(anomaly_matcher, AnomalyScoreMatcher)
        assert anomaly_matcher.source == "INFERENCE_GATEWAY_ISOLATION_FOREST"
        assert anomaly_matcher.score_operator == "GT"
        assert anomaly_matcher.threshold == 0.75
        
        # Test enhanced governance action fields
        assert pir.governance_actions[0].execution_order == 1
    
    def test_pir_create_and_update(self, valid_pir_data):
        """Test PIR create and update models."""
        # Test PIRCreate
        pir_create = PIRCreate(**valid_pir_data)
        assert pir_create.name == "Test Policy"
        assert pir_create.version == 1
        assert pir_create.version_id == "test-policy-v1.0.0"  # New v2 field
        
        # Test PIRUpdate
        update_data = {
            "name": "Updated Policy",
            "status": PolicyStatus.ACTIVE,
            "priority": 90,
            "updated_by": "admin-user",
            # New v2 fields in update
            "version_id": "test-policy-v1.1.0",
            "source_regulation_references": [{"sourceId": "CCPA Section 1798", "jurisdiction": "US-CA"}],
            "temporal_logic_annotations": TemporalLogicAnnotations(
                ltl_specifications=[LTLSpecification(
                    property_id="updated-prop-001",
                    formula="G (sensitive_data_request -> X approval_required)"
                )]
            )
        }
        pir_update = PIRUpdate(**update_data)
        assert pir_update.name == "Updated Policy"
        assert pir_update.status == PolicyStatus.ACTIVE
        assert pir_update.priority == 90
        assert pir_update.updated_by == "admin-user"
        assert pir_update.description is None  # Not updated
        # Test new v2 fields in update
        assert pir_update.version_id == "test-policy-v1.1.0"
        assert pir_update.source_regulation_references[0]["sourceId"] == "CCPA Section 1798"
        assert len(pir_update.temporal_logic_annotations.ltl_specifications) == 1

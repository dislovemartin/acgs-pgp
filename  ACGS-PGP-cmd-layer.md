## 1. ACGS-PGP: P-IR (Prompt Intermediate Representation) Schema Document

**Document Version:** 2.0 (Aligning with Regulith Command Cycle 2.0)
**Date:** May 15, 2025
**Status:** DRAFT (Derived from ACGS-PGP Spec v2.0)

**Table of Contents:**

1.  **Introduction**
    1.1. Purpose (As per ACGS-PGP Spec v2.0 Sec 2.3)
    1.2. Scope
    1.3. Audience
    1.4. Definitions (P-IR, PGS-AI, RGE, LTL, CTL, HE, PQC)
    1.5. Document Versioning & Relation to ACGS-PGP Spec v2.0
2.  **P-IR Core Philosophy & Design Principles (Derived from ACGS-PGP Spec v2.0 Sec 2.3)**
    2.1. Machine Executability for RGE (Wasm target)
    2.2. Human Readability & Auditability
    2.3. Extensibility for Future Governance Primitives
    2.4. Support for Formal Verification Annotations (LTL/CTL)
    2.5. Integration with Cryptographic Primitives (HE, PQC Signatures)
    2.6. Neo4j Graph Database Compatibility (Nodes, Relationships, Properties)
3.  **P-IR JSON Schema Definition (`pir_v2.schema.json`)**
4.  **Detailed Field Descriptions & Semantics (Elaborating on ACGS-PGP Spec v2.0 Sec 2.3)**
    4.1. Top-Level P-IR Object
    4.2. `metadata` Object (including `pqcSignature`, `formalVerification`, `hePolicy`)
    4.3. `scope` Object
    4.4. `triggerConditions` Object (including `semanticSimilarity`, `anomalyScore`)
    4.5. `governanceActions` Array Objects (including `invokeSecureTool`, `initiateSMPC`)
    4.6. `temporalLogicAnnotations` Object (LTL/CTL)
    4.7. `quantumOptimizationHints` Object (for D-Wave)
5.  **P-IR Lifecycle Statuses & Transitions**
6.  **Example P-IR Instances (Illustrating Advanced Features)**
    6.1. Example 1: P-IR with LTL Annotation for Safety Property
    6.2. Example 2: P-IR with HE Policy for Sensitive Data in Triggers
    6.3. Example 3: P-IR Governing an SMPC-enabled Tool
    6.4. Example 4: P-IR with Quantum Optimization Hint for Clause Selection
7.  **Schema Versioning and Evolution Strategy (for `pir_v2.schema.json`)**

---

### 1. Introduction

#### 1.1. Purpose
This document specifies the definitive JSON schema for the Prompt Intermediate Representation (P-IR) Version 2.0, as conceptualized within the ACGS-PGP Spec v2.0. The P-IR is a structured, machine-executable format embodying governance policies, designed for synthesis by the Hybrid PGS-AI and enforcement by the Wasm-based Runtime Governance Engine (RGE). It is central to achieving "Compliance by Design—executable, auditable, and immutable" [ACGS-PGP Spec v2.0 Sec 1.0].

#### 1.2. Scope
This schema applies to all P-IRs generated, stored, versioned (in Neo4j), streamed (via Kafka/Flink), and enforced within the ACGS-PGP Command Layer. It underpins the entire governance lifecycle, from regulatory text ingestion to runtime AI Constitution compilation.

#### 1.3. Audience
(As previously defined, with added emphasis on teams working with Neo4j, Wasm RGE, Formal Verification, and Quantum Optimization modules.)

#### 1.4. Definitions
*   **P-IR:** Prompt Intermediate Representation (v2.0).
*   **PGS-AI:** Hybrid Governance Synthesizer AI (Llama/Grok + Symbolic + SMPC, orchestrated by AIQ Toolkit).
*   **RGE:** Runtime Governance Engine (Wasm-based, GPU-accelerated, HE-capable).
*   **LTL:** Linear Temporal Logic (for formal property specification).
*   **CTL:** Computation Tree Logic (alternative temporal logic).
*   **HE:** Homomorphic Encryption.
*   **PQC:** Post-Quantum Cryptography.
*   **Neo4j:** Graph database for storing P-IRs as a knowledge graph.
*   **AIQ Toolkit:** Agent Intelligence Toolkit used for PGS-AI workflow development.

#### 1.5. Document Versioning & Relation to ACGS-PGP Spec v2.0
This P-IR Schema Document (v2.0) directly implements and elaborates upon the P-IR concepts described in ACGS-PGP Spec v2.0, particularly Section 2.3 ("The P-IR: Compilable Governance Artifacts").

### 2. P-IR Core Philosophy & Design Principles

The P-IR v2.0 design adheres to the following principles derived from ACGS-PGP Spec v2.0:

*   **2.1. Machine Executability:** Directly translatable into efficient Wasm RGE logic.
*   **2.2. Human Readability & Auditability:** Structured JSON with clear descriptions, linkable to source regulations and AI Constitution articles, and auditable via AuditKit.
*   **2.3. Extensibility:** Allows for new trigger types, action types, and metadata fields as governance needs evolve.
*   **2.4. Support for Formal Verification:** Includes dedicated fields for LTL/CTL annotations to enable model checking of policy properties [ACGS-PGP Spec v2.0 Sec 2.2, 4.4].
*   **2.5. Integration with Cryptographic Primitives:** Supports fields for PQC signatures (for integrity/authenticity) and HE policies (for processing sensitive P-IR data within the RGE) [ACGS-PGP Spec v2.0 Sec 4.3].
*   **2.6. Neo4j Graph Database Compatibility:** Schema elements are designed to map effectively to a graph structure (nodes for clauses, regulations; relationships for derivation, precedence) [ACGS-PGP Spec v2.0 Sec 3.3].

### 3. P-IR JSON Schema Definition (`pir_v2.schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ACGS-PGP Prompt Intermediate Representation (P-IR) v2.0",
  "description": "Schema for a governance rule within the ACGS-PGP Command Layer, supporting formal verification, PQC, and HE.",
  "type": "object",
  "properties": {
    "pirId": {
      "description": "Unique identifier for this P-IR (immutable across versions).",
      "type": "string",
      "format": "uuid"
    },
    "versionId": {
      "description": "Unique identifier for this specific version of the P-IR (e.g., pirId_vX.Y.Z). Stored as a node in Neo4j.",
      "type": "string"
    },
    "name": {
      "description": "A short, human-readable name for the policy.",
      "type": "string",
      "maxLength": 256
    },
    "description": {
      "description": "A human-readable description of the policy's purpose and intent.",
      "type": "string"
    },
    "status": {
      "description": "The current lifecycle status of this P-IR version.",
      "type": "string",
      "enum": ["DRAFT", "PENDING_VALIDATION", "PENDING_FV", "ACTIVE", "SUPERSEDED", "ARCHIVED", "REJECTED"]
    },
    "aiConstitutionReferences": {
      "description": "An array of identifiers linking this P-IR to specific articles in the AI Constitution.",
      "type": "array",
      "items": { "type": "string" },
      "default": []
    },
    "sourceRegulationReferences": {
      "description": "References to external regulations or source documents this P-IR is derived from (Neo4j relationship).",
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "sourceId": { "type": "string", "description": "Unique ID of the source document/regulation section." },
          "jurisdiction": { "type": "string" },
          "specificClause": { "type": "string" }
        },
        "required": ["sourceId"]
      },
      "default": []
    },
    "scope": {
      "$ref": "#/definitions/Scope"
    },
    "triggerConditions": {
      "$ref": "#/definitions/TriggerConditions"
    },
    "governanceActions": {
      "description": "An ordered list of actions to be taken. Actions are executed sequentially.",
      "type": "array",
      "items": { "$ref": "#/definitions/GovernanceAction" },
      "minItems": 1
    },
    "priority": {
      "description": "Policy priority for conflict resolution (0-1000, higher is more critical). RGE uses this with DistilBERT precedence scores.",
      "type": "integer",
      "default": 500,
      "minimum": 0,
      "maximum": 1000
    },
    "severity": {
      "description": "Severity of the issue this policy addresses.",
      "type": "string",
      "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"],
      "default": "MEDIUM"
    },
    "tags": {
      "description": "Arbitrary tags for categorization.",
      "type": "array",
      "items": { "type": "string" },
      "default": []
    },
    "temporalLogicAnnotations": {
      "$ref": "#/definitions/TemporalLogicAnnotations"
    },
    "homomorphicEncryptionPolicy": {
      "$ref": "#/definitions/HomomorphicEncryptionPolicy"
    },
    "quantumOptimizationHints": {
      "$ref": "#/definitions/QuantumOptimizationHints"
    },
    "metadata": {
      "$ref": "#/definitions/PIRMetadata"
    }
  },
  "required": [
    "pirId",
    "versionId",
    "name",
    "description",
    "status",
    "scope",
    "triggerConditions",
    "governanceActions",
    "priority",
    "metadata"
  ],
  "definitions": {
    "Scope": {
      "description": "Defines the applicability of the policy.",
      "type": "object",
      "properties": {
        "llmModels": { "$ref": "#/definitions/InclusionExclusionList" },
        "userRoles": { "$ref": "#/definitions/InclusionExclusionList" },
        "applications": { "$ref": "#/definitions/InclusionExclusionList" },
        "dataSensitivityLevels": {
          "type": "object",
          "properties": {
            "levels": { "type": "array", "items": { "type": "string" } },
            "matchType": { "type": "string", "enum": ["ANY_OF", "ALL_OF", "MINIMUM_LEVEL"], "default": "ANY_OF" },
            "levelOrder": { "type": "array", "items": { "type": "string" }, "description": "Ordered list of sensitivity levels if matchType is MINIMUM_LEVEL."}
          }
        },
        "customAttributes": {
            "type": "array",
            "items": { "$ref": "#/definitions/ContextAttributeMatcher"}
        }
      },
      "additionalProperties": false
    },
    "InclusionExclusionList": {
      "type": "object",
      "properties": {
        "include": { "type": "array", "items": { "type": "string" } },
        "exclude": { "type": "array", "items": { "type": "string" } }
      }
    },
    "TriggerConditions": {
      "description": "Conditions that activate the policy.",
      "type": "object",
      "properties": {
        "operator": { "type": "string", "enum": ["AND", "OR"], "default": "AND" },
        "conditions": {
          "type": "array",
          "items": {
            "type": "object",
            "oneOf": [
              { "$ref": "#/definitions/PromptPatternMatcher" },
              { "$ref": "#/definitions/ContextAttributeMatcher" },
              { "$ref": "#/definitions/ToolUsageMatcher" },
              { "$ref": "#/definitions/ResponsePatternMatcher" },
              { "$ref": "#/definitions/AnomalyScoreMatcher" }
            ]
          }
        }
      },
      "required": ["operator", "conditions"],
      "minProperties": 1
    },
    "PromptPatternMatcher": {
      "type": "object",
      "properties": {
        "type": { "const": "PROMPT_PATTERN" },
        "patternType": { "type": "string", "enum": ["REGEX", "KEYWORD_LIST", "SEMANTIC_SIMILARITY"] },
        "value": { "type": ["string", "array"], "items": { "type": "string"} },
        "matchCase": { "type": "boolean", "default": false },
        "similarityThreshold": { "type": "number", "minimum": 0, "maximum": 1 },
        "embeddingModelId": { "type": "string", "description": "Model used for semantic similarity."}
      },
      "required": ["type", "patternType", "value"]
    },
    "ContextAttributeMatcher": {
      "type": "object",
      "properties": {
        "type": { "const": "CONTEXT_ATTRIBUTE" },
        "attributeName": { "type": "string" },
        "operator": { "type": "string", "enum": ["EQUALS", "NOT_EQUALS", "CONTAINS", "IN_LIST", "GT", "LT", "GTE", "LTE", "REGEX_MATCH"] },
        "value": { "type": ["string", "number", "boolean", "array"] }
      },
      "required": ["type", "attributeName", "operator", "value"]
    },
    "ToolUsageMatcher": {
      "type": "object",
      "properties": {
        "type": { "const": "TOOL_USAGE_REQUEST" },
        "toolName": { "type": "string" },
        "parameterMatchers": {
          "type": "array",
          "items": { "$ref": "#/definitions/ContextAttributeMatcher" }
        }
      },
      "required": ["type", "toolName"]
    },
    "ResponsePatternMatcher": {
      "type": "object",
      "properties": {
        "type": { "const": "RESPONSE_PATTERN" },
        "patternType": { "type": "string", "enum": ["REGEX", "KEYWORD_LIST", "SEMANTIC_SIMILARITY", "TOXICITY_SCORE", "PII_DETECTED_TYPE"] },
        "value": { "type": ["string", "array", "number"], "items": { "type": "string"} },
        "matchCase": { "type": "boolean", "default": false },
        "similarityThreshold": { "type": "number", "minimum": 0, "maximum": 1 },
        "scoreOperator": { "type": "string", "enum": ["GT", "LT", "GTE", "LTE"], "description": "For TOXICITY_SCORE" },
        "piiTypes": { "type": "array", "items": {"type": "string"}, "description": "For PII_DETECTED_TYPE, e.g., ['EMAIL', 'PHONE_NUMBER']"}
      },
      "required": ["type", "patternType", "value"]
    },
    "AnomalyScoreMatcher": {
        "type": "object",
        "properties": {
            "type": { "const": "ANOMALY_SCORE" },
            "source": { "type": "string", "enum": ["INFERENCE_GATEWAY_ISOLATION_FOREST", "CUSTOM_DETECTOR"]},
            "scoreOperator": { "type": "string", "enum": ["GT", "GTE"]},
            "threshold": { "type": "number" }
        },
        "required": ["type", "source", "scoreOperator", "threshold"]
    },
    "GovernanceAction": {
      "type": "object",
      "properties": {
        "actionType": {
          "type": "string",
          "enum": [
            "ALLOW", "BLOCK", "REDACT_PROMPT", "REDACT_RESPONSE",
            "TRANSFORM_PROMPT_PREPEND", "TRANSFORM_PROMPT_APPEND", "TRANSFORM_PROMPT_REPLACE",
            "TRANSFORM_RESPONSE_PREPEND", "TRANSFORM_RESPONSE_APPEND",
            "LOG_EVENT", "ALERT_ADMINS", "REQUIRE_HUMAN_APPROVAL",
            "INVOKE_SECURE_GOVERNANCE_TOOL", "INITIATE_SMPC_PROTOCOL", "OVERRIDE_LLM_RESPONSE"
          ]
        },
        "parameters": { "type": "object", "additionalProperties": true },
        "executionOrder": { "type": "integer", "description": "Defines sequence if multiple actions of same type or for complex interactions."}
      },
      "required": ["actionType", "executionOrder"]
    },
    "TemporalLogicAnnotations": {
      "type": "object",
      "properties": {
        "ltlSpecifications": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "propertyId": { "type": "string", "description": "Unique ID for this LTL property." },
              "formula": { "type": "string", "description": "The LTL formula." },
              "description": { "type": "string" },
              "variablesMapping": { "type": "object", "additionalProperties": { "type": "string" }, "description": "Maps LTL variables to P-IR context/action fields."}
            },
            "required": ["propertyId", "formula"]
          }
        },
        "ctlSpecifications": {
            "type": "array",
            "items": { /* Similar structure to LTL */ }
        }
      }
    },
    "HomomorphicEncryptionPolicy": {
      "type": "object",
      "properties": {
        "fieldsToEncrypt": {
          "type": "array",
          "items": { "type": "string", "description": "JSONPath to fields within this P-IR to be HE encrypted (e.g., 'triggerConditions.conditions[0].value')." }
        },
        "heSchemeId": { "type": "string", "description": "Identifier of the HE scheme and parameters to be used." },
        "keyManagementPolicyId": { "type": "string", "description": "Policy for managing HE keys related to this P-IR."}
      }
    },
    "QuantumOptimizationHints": {
        "type": "object",
        "properties": {
            "quboFormulationHint": { "type": "string", "description": "Hint for QUBO model generation for D-Wave (e.g., 'prioritize_blocking_actions')."},
            "targetObjective": { "type": "string", "description": "Objective for optimization (e.g., 'minimize_false_positives_for_pii')."}
        }
    },
    "PIRMetadata": {
      "type": "object",
      "properties": {
        "author": { "type": "string" },
        "createdTimestampUtc": { "type": "string", "format": "date-time" },
        "lastUpdatedTimestampUtc": { "type": "string", "format": "date-time" },
        "pqcSignature": {
            "type": "object",
            "properties": {
                "algorithm": { "type": "string", "enum": ["CRYSTALS-Dilithium2", "Falcon-512"] },
                "signatureValue": { "type": "string", "format": "byte" },
                "publicKeyId": { "type": "string" }
            }
        },
        "formalVerification": {
            "type": "object",
            "properties": {
                "lastRunId": {"type": "string", "format": "uuid"},
                "status": { "type": "string", "enum": ["NOT_VERIFIED", "VERIFIED", "FALSIFIED", "ERROR"] },
                "verifiedTimestampUtc": { "type": "string", "format": "date-time" },
                "verifiedProperties": { "type": "array", "items": {"type": "string"}, "description": "List of LTL/CTL property IDs that were verified."}
            }
        },
        "synthesisDetails": {
          "type": "object",
          "properties": {
            "pgsAiModelId": { "type": "string" },
            "aiqWorkflowRunId": { "type": "string" },
            "inputHash": { "type": "string", "description": "Hash of the input intent/document." },
            "confidenceScore": { "type": "number", "minimum": 0, "maximum": 1 }
          }
        }
      },
      "required": ["createdTimestampUtc", "lastUpdatedTimestampUtc"]
    }
  }
}
```

### 4. Detailed Field Descriptions & Semantics

*(This section would elaborate on each field from the JSON schema above, providing examples and explaining its role, especially for new fields like `temporalLogicAnnotations`, `homomorphicEncryptionPolicy`, `quantumOptimizationHints`, and the PQC/FV fields within `metadata`. It would also detail how `triggerConditions.conditions.oneOf` works and the parameters for new `governanceActions` like `INVOKE_SECURE_GOVERNANCE_TOOL` and `INITIATE_SMPC_PROTOCOL`.)*

*   **`pirId` (string, uuid, required):** Immutable unique identifier for the logical P-IR.
*   **`versionId` (string, required):** Unique identifier for this *version* of the P-IR (e.g., `PIR_ID_v1.2.3` or a UUID). This is the primary key for the versioned P-IR node in Neo4j.
*   **`metadata.pqcSignature` (object):**
    *   `algorithm` (string, enum): Specifies the PQC signature algorithm used (e.g., `CRYSTALS-Dilithium2`, `Falcon-512`) as per ACGS-PGP Spec v2.0 Sec 4.3.
    *   `signatureValue` (string, base64): The PQC signature of the canonicalized P-IR content (excluding the signature itself).
    *   `publicKeyId` (string): Identifier of the PQC public key used for verification.
*   **`metadata.formalVerification` (object):**
    *   `lastRunId` (string, uuid): Link to the AuditKit event ID of the last formal verification run for this P-IR version.
    *   `status` (string, enum): Current verification status.
    *   `verifiedProperties` (array of strings): List of `propertyId`s from `temporalLogicAnnotations` that have been successfully verified.
*   **`metadata.synthesisDetails.aiqWorkflowRunId` (string):** If synthesized via AIQ Toolkit, the run ID of the AIQ workflow.
*   **`scope.customAttributes` (array of `ContextAttributeMatcher`):** Allows for complex, reusable attribute-based scoping conditions.
*   **`triggerConditions.conditions.oneOf`:** Each item in the `conditions` array must match one of the defined matcher schemas (e.g., `PromptPatternMatcher`, `AnomalyScoreMatcher`).
*   **`triggerConditions.conditions[...].AnomalyScoreMatcher`:**
    *   `source` (string, enum): Indicates the origin of the anomaly score (e.g., `INFERENCE_GATEWAY_ISOLATION_FOREST`).
    *   `scoreOperator` (string, enum): `GT`, `GTE`.
    *   `threshold` (number): The anomaly score threshold.
*   **`governanceActions.actionType.INVOKE_SECURE_GOVERNANCE_TOOL`:**
    *   `parameters.toolId` (string): ID of the tool registered in Tool Management Service.
    *   `parameters.inputMapping` (object): How to map P-IR context/prompt to tool inputs.
    *   `parameters.heContextId` (string, optional): If tool operates on HE data.
*   **`governanceActions.actionType.INITIATE_SMPC_PROTOCOL`:**
    *   `parameters.protocolId` (string): Identifier of the SMPC protocol.
    *   `parameters.participantInputs` (object): Mapping of required inputs for participants.
*   **`temporalLogicAnnotations` (object):**
    *   `ltlSpecifications` / `ctlSpecifications` (array of objects):
        *   `propertyId` (string): Unique ID for this formal property.
        *   `formula` (string): The LTL/CTL formula.
        *   `description` (string): Human-readable meaning of the property.
        *   `variablesMapping` (object): Maps variables in the formula to specific P-IR fields or runtime context variables (e.g., `{"p": "triggerConditions.conditions.isActive", "q": "runtimeContext.userRole"}`).
*   **`homomorphicEncryptionPolicy` (object):** [ACGS-PGP Spec v2.0 Sec 4.3]
    *   `fieldsToEncrypt` (array of string JSONPaths): Specifies which P-IR fields (e.g., sensitive patterns in `triggerConditions`) should be stored/transmitted encrypted and processed by the RGE using HE.
    *   `heSchemeId` (string): Identifier for the HE scheme (e.g., `BFV_SET1`, `CKKS_SET2`) and parameters managed by a Crypto Service/KMS.
*   **`quantumOptimizationHints` (object):** [ACGS-PGP Spec v2.0 Sec 2.3]
    *   `quboFormulationHint` (string): Provides guidance to the D-Wave interface on how to translate this P-IR (or parts of it) into a QUBO model for optimization tasks (e.g., optimal clause selection under constraints).
    *   `targetObjective` (string): The objective this P-IR contributes to when considered for quantum optimization (e.g., "minimize_risk_score_X").

### 5. P-IR Lifecycle Statuses & Transitions

*   **`DRAFT`**: Initial creation, or after rejection/superseding if being revised.
*   **`PENDING_VALIDATION`**: Submitted for human expert review (legal, ethical, technical).
*   **`PENDING_FV`**: (Optional state after validation) Submitted for formal verification if LTL/CTL annotations are present and FV is mandated.
*   **`ACTIVE`**: Approved, (optionally) formally verified, and live for RGE enforcement.
*   **`SUPERSEDED`**: Replaced by a new `versionId` of the same `pirId`. Not active.
*   **`ARCHIVED`**: No longer relevant, kept for historical audit. Not active.
*   **`REJECTED`**: Failed validation or FV. Can be moved to `DRAFT` for revision or `ARCHIVED`.

*(Flow diagram of statuses would be beneficial here)*

### 6. Example P-IR Instances

#### 6.1. Example 1: P-IR with LTL Annotation for Safety Property

```json
{
  "pirId": "safety-001-pir",
  "versionId": "safety-001-pir_v1.0.0",
  "name": "Ensure LLM Acknowledges Uncertainty",
  "description": "If LLM response confidence is low, it must state its uncertainty.",
  "status": "ACTIVE",
  "scope": { "llmModels": { "include": ["model-alpha"] } },
  "triggerConditions": {
    "operator": "AND",
    "conditions": [
      {
        "type": "CONTEXT_ATTRIBUTE",
        "attributeName": "llmResponse.confidenceScore",
        "operator": "LT",
        "value": 0.6
      }
    ]
  },
  "governanceActions": [
    {
      "actionType": "TRANSFORM_RESPONSE_PREPEND",
      "parameters": { "text": "As an AI, I have limited information and my confidence in this response is moderate. " },
      "executionOrder": 1
    }
  ],
  "priority": 200,
  "severity": "MEDIUM",
  "metadata": { /* ... standard metadata ... */
    "formalVerification": { "status": "VERIFIED", "verifiedProperties": ["ltl-uncertainty-ack"] }
  },
  "temporalLogicAnnotations": {
    "ltlSpecifications": [{
      "propertyId": "ltl-uncertainty-ack",
      "formula": "G ( (llmResponse.confidenceScore < 0.6) -> X (response.startsWith('As an AI...')) )",
      "description": "Globally, if response confidence is low, the next state (final response) must start with the uncertainty preamble.",
      "variablesMapping": {
          "llmResponse.confidenceScore": "runtimeContext.llmInternalMetrics.confidence",
          "response.startsWith": "runtimeOutput.finalResponse.startsWith"
      }
    }]
  }
}
```

#### 6.2. Example 2: P-IR with HE Policy for Sensitive Data in Triggers

```json
{
  "pirId": "he-pii-filter-002",
  "versionId": "he-pii-filter-002_v1.1.0",
  "name": "Filter Prompts with Encrypted Watchlist Terms",
  "description": "Uses HE to check if prompt contains terms from an encrypted watchlist.",
  "status": "ACTIVE",
  "scope": {},
  "triggerConditions": {
    "operator": "AND",
    "conditions": [
      {
        "type": "CONTEXT_ATTRIBUTE", // This would be a special HE-enabled context attribute
        "attributeName": "prompt.heEncryptedMatch.watchlistId_XYZ", // RGE knows this needs HE
        "operator": "EQUALS", // HE equality check
        "value": true // The HE operation returns true if a match
      }
    ]
  },
  "governanceActions": [
    { "actionType": "BLOCK", "parameters": { "messageToUser": "Request blocked due to sensitive content match." }, "executionOrder": 1 }
  ],
  "priority": 700,
  "severity": "CRITICAL",
  "metadata": { /* ... standard metadata ... */
    "pqcSignature": { "algorithm": "Dilithium2", "signatureValue": "...", "publicKeyId": "..."}
  },
  "homomorphicEncryptionPolicy": {
    "fieldsToEncrypt": [], // The actual watchlist terms are encrypted server-side; RGE receives encrypted prompt features
    "heSchemeId": "BFV_PII_Watchlist_Scheme",
    "keyManagementPolicyId": "KMS_Policy_HE_Watchlist"
  }
}
```
*(Further examples for SMPC and Quantum Hints would follow similar detailed structures, referencing their specific parameters as outlined in section 4.)*

### 7. Schema Versioning and Evolution Strategy
(As previously defined, emphasizing that P-IR v2.0 is a major version change due to the introduction of LTL, HE, PQC, and advanced trigger/action types. Migration scripts and RGE backward compatibility (or phased rollout) will be critical.)

---

## 2. ACGS-PGP: System Architecture Document

**Document Version:** 2.0 (Aligning with Regulith Command Cycle 2.0)
**Date:** May 15, 2025
**Status:** DRAFT (Derived from ACGS-PGP Spec v2.0)

**Table of Contents:** (Extending previous TOC with Spec v2.0 details)

1.  **Introduction**
    1.1. Purpose (Operationalizing ACGS-PGP Command Layer)
    1.2. Scope (All components in Spec v2.0, including advanced crypto, FV, Quantum)
    1.3. Audience
    1.4. Guiding Architectural Principles (Modularity, Sub-Millisecond Governance, Uncompromising Security, Verifiable Compliance, Immutable Auditability, Edge Optimization, Serverless Elasticity, Zero-Trust Command) [ACGS-PGP Spec v2.0 Sec 1.0]
    1.5. Relationship to other Documents
    1.6. Definitions and Acronyms (Expanded for Spec v2.0 technologies)
2.  **Platform Overview (Command Layer)**
    2.1. Core Mission and Capabilities (Realizing "Law in every loop")
    2.2. Logical Architecture Diagram (Echelon-based, as per ACGS-PGP Spec v2.0 Sec 3.1, using provided Mermaid)
    2.3. Key Technology Choices (DLT, Kafka/Flink, Neo4j, Hybrid PGS-AI, Wasm RGE, PQC, HE, SMPC, NuSMV, D-Wave, AIQ Toolkit) [ACGS-PGP Spec v2.0 Sec 2.1]
3.  **Component Architecture Details (Elaborating on ACGS-PGP Spec v2.0 Sec 3.2)**
    3.1. **Echelon 1: Global Policy Intelligence & Synthesis**
        *   3.1.1. External Feeds & Kafka/Flink Pipeline (Normalization, Diffing, P-IR Synthesis Triggers)
        *   3.1.2. Hybrid PGS-AI (Llama/Grok + Symbolic AI + SMPC, AIQ Toolkit Orchestration)
            *   AIQ Workflow Design (Intent Extraction, Symbolic Refinement, LTL Annotation, Graph Construction)
            *   SMPC Coordination for distributed/private synthesis
        *   3.1.3. P-IR Graph Database (Neo4j) (Versioned P-IRs, LTL/CTL annotations, relationships)
    3.2. **Echelon 2: Edge Governance Compilation & Enforcement**
        *   3.2.1. Inference Gateway (Celery/Redis, Akamai CDN, Isolation Forest, PQC Termination)
        *   3.2.2. Wasm RGE (Rust/C++, Serverless Edge, GPU, DistilBERT, LTL Parser, HE Module)
            *   Wasm Runtime Environment (e.g., Wasmtime, WasmEdge)
            *   GPU Acceleration Strategy (CUDA via Wasm host or direct bindings)
            *   HE Module Integration (SEAL/PALISADE wrapper)
        *   3.2.3. Application LLM Interface
        *   3.2.4. AI Constitution Registry (OCI-Compliant, for Wasm RGE modules)
    3.3. **Echelon 3: Immutable Audit & Verification**
        *   3.3.1. AuditKit (Hyperledger Fabric) (Chaincode for events, CLI/UI, PQC Signatures)
        *   3.3.2. Formal Verification Module (NuSMV Wrapper) (P-IR to SMV, LTL/CTL checking)
    3.4. **Cross-Cutting Components**
        *   3.4.1. Cryptographic Services (PQC, HE, SMPC modules/libraries)
        *   3.4.2. Quantum Optimization Interface (D-Wave Leap API)
        *   3.4.3. Monitoring & Observability Stack (Prometheus, Grafana, OpenTelemetry for AIQ)
        *   3.4.4. Identity Management (SPIFFE/SPIRE for Zero-Trust service identity)
4.  **Inter-Component Communication & Data Flows (Elaborating on ACGS-PGP Spec v2.0 Sec 3.3, 4.0)**
    4.1. Synchronous Communication (gRPC with PQC, GraphQL for Neo4j)
    4.2. Asynchronous Communication (Kafka Topics: `raw_regulatory_feeds`, `pir_synthesis_triggers`, `pir_graph_updates`, `rge_wasm_publish_events`, `governance_events_for_auditkit`, `fv_requests`, `fv_results`)
    4.3. Data Formats & Schemas (P-IR v2.0, NormalizedRegulationEvent, AuditKitEvent, AIConstitutionWasmManifest)
    4.4. Detailed Data Flow Diagrams (As per provided Mermaid diagrams, embedded and referenced)
5.  **Data Management Architecture**
    5.1. Neo4j P-IR Graph (Schema, Versioning, Querying for RGE)
    5.2. Hyperledger Fabric Ledger (AuditKit Event Data Model)
    5.3. Kafka Stream Persistence and Retention
    5.4. HE Ciphertext Management & Key Storage (Integration with KMS)
6.  **Security Architecture (Reference to dedicated Security Architecture Document)**
    *   _Summary of PQC, HE, SMPC, Zero-Trust (SPIFFE/SPIRE) application._
7.  **Scalability, Performance, and Resilience (Targets from ACGS-PGP Spec v2.0 KSOs)**
    7.1. RGE Edge Scalability (Serverless auto-scaling, Wasm startup)
    7.2. PGS-AI Scalability (AIQ distributed tasks, SMPC scaling)
    7.3. Kafka/Flink & Neo4j Scalability
    7.4. Resilience Patterns for Advanced Components (e.g., fallback for HE failure, circuit breakers for D-Wave calls)
8.  **Deployment Architecture (Kubernetes & Serverless Edge)**
    8.1. K8s for Echelon 1 & 3 components (PGS-AI, Neo4j, Kafka, Fabric, FV Module).
    8.2. Serverless (Lambda/Workers) for Echelon 2 RGE Wasm modules.
    8.3. Edge Orchestrator for RGE Wasm deployment and updates to edge locations/CDNs.
9.  **Observability Strategy for Distributed & Advanced Components**
    9.1. AIQ Toolkit Observability for PGS-AI (Metrics, Traces, Logs).
    9.2. Monitoring Wasm RGE execution at the edge.
    9.3. Tracing PQC/HE/SMPC operations.
10. **Integration with AIQ Toolkit (for PGS-AI)**
    10.1. AIQ Workflow definitions for P-IR synthesis.
    10.2. Custom AIQ Tools for symbolic reasoning, LTL generation, SMPC stubs, Neo4j interaction.
    10.3. Leveraging AIQ for PGS-AI profiling, debugging, and evaluation.
11. **Future Architectural Evolution (Quantum, Advanced AI Governance)**
    11.1. Roadmap for deeper D-Wave integration.
    11.2. Integration points for future AI-driven constitutional evolution.

---
*(Content for System Architecture Document would continue, elaborating each point based on ACGS-PGP Spec v2.0, including the Mermaid diagrams provided earlier.)*

### 2.2. Logical Architecture Diagram (Echelon-based)
(Embedding the Mermaid diagram from ACGS-PGP Spec v2.0 Sec 3.1, as provided in the previous turn)

```mermaid
graph TD
    subgraph Echelon 1: Global Policy Intelligence & Synthesis (Cloud Backend)
        direction LR
        ExtFeeds[External Regulatory Feeds/Threat Intel] --> KafkaFlink[Kafka/Flink Pipeline<br/><i>Normalization, Diffing, Triggering</i>]
        KafkaFlink --> SMPC_PGS_AI[SMPC-Orchestrated Hybrid PGS-AI<br/><i>Llama/Grok + OWL/SHACL (AIQ Toolkit Workflow)</i>]
        SMPC_PGS_AI --> Neo4j_PIR_DB[P-IR Graph DB (Neo4j)<br/><i>Versioned P-IRs, LTL Annotations</i>]
    end

    subgraph Echelon 2: Edge Governance Compilation & Enforcement (Edge/Serverless)
        direction LR
        ClientApp[Client Application] --> InferenceGateway[Inference Gateway<br/><i>Celery/Redis, Akamai CDN Cache, Isolation Forest</i>]
        Neo4j_PIR_DB -- P-IRs / CDN Miss --> InferenceGateway
        InferenceGateway -- Context + P-IR (from Cache/Neo4j) --> RGE_Wasm[RGE (Wasm on Serverless Edge)<br/><i>GPU, DistilBERT, LTL Parser, HE Module</i>]
        RGE_Wasm -- AI Constitution --> AppLLM[Application LLM]
        InferenceGateway -- Governed Traffic --> AppLLM
        AppLLM -- Response --> InferenceGateway
        InferenceGateway -- Governed Response --> ClientApp
    end

    subgraph Echelon 3: Immutable Audit & Verification (Distributed Ledger & Central Tools)
        direction LR
        InferenceGateway -- Governance Events --> AuditKit_Fabric[AuditKit (Hyperledger Fabric)<br/><i>CLI/UI, Audit Replay</i>]
        Neo4j_PIR_DB -- P-IRs for Verification --> FormalVerificationModule[Formal Verification Module<br/><i>NuSMV Wrapper, LTL/CTL Checker</i>]
        FormalVerificationModule -- Verification Status --> Neo4j_PIR_DB
    end

    subgraph Cross-Cutting Security & Operations
        PQC_APIs[PQC for External APIs (CRYSTALS-Kyber)]
        HE_PIR_Processing[HE for P-IR in RGE (SEAL/PALISADE)]
        SMPC_PGS_Synthesis[SMPC for PGS-AI Synthesis]
        Quantum_PIR_Opt[D-Wave for P-IR Optimization (Prototype)]
        Monitoring[Prometheus/Grafana]
        Identity[SPIFFE/SPIRE (Implied for Zero-Trust)]
    end

    ExtFeeds --> KafkaFlink
    KafkaFlink --> SMPC_PGS_AI
    SMPC_PGS_AI --> Neo4j_PIR_DB

    ClientApp --> InferenceGateway
    InferenceGateway --> RGE_Wasm
    RGE_Wasm -.-> InferenceGateway
    InferenceGateway -.-> AppLLM
    AppLLM -.-> InferenceGateway
    InferenceGateway -.-> ClientApp

    InferenceGateway --> AuditKit_Fabric
    Neo4j_PIR_DB --> FormalVerificationModule
    FormalVerificationModule --> Neo4j_PIR_DB

    PQC_APIs <--> InferenceGateway
    HE_PIR_Processing <--> RGE_Wasm
    SMPC_PGS_Synthesis <--> SMPC_PGS_AI
```

### 3. Component Architecture Details (Elaborating on ACGS-PGP Spec v2.0 Sec 3.2)

#### 3.1. Echelon 1: Global Policy Intelligence & Synthesis
*   **3.1.1. External Feeds & Kafka/Flink Pipeline:**
    *   **Responsibilities:** Ingest diverse external data (regulatory updates, threat intelligence feeds like STIX/TAXII, internal policy documents). Normalize data into a `NormalizedRegulationEvent` schema. Perform real-time analysis (e.g., diffing against existing P-IR knowledge graph in Neo4j) using Apache Flink to identify significant changes. Trigger P-IR synthesis workflows in PGS-AI via Kafka.
    *   **Technologies:** Apache Kafka, Kafka Connectors, Apache Flink (SQL/DataStream API).
*   **3.1.2. Hybrid PGS-AI (Llama/Grok + Symbolic AI + SMPC, AIQ Toolkit Orchestration):**
    *   **Responsibilities:** Translate `NormalizedRegulationEvent` or direct policy intents into structured P-IR v2.0 objects. This involves:
        *   **LLM Intent Extraction (AIQ Tool):** Fine-tuned Llama/Grok (4-bit quantized, running as a NIM or similar inference server) extracts entities, relationships, deontic modalities, and draft P-IR structures.
        *   **Symbolic Refinement & LTL Annotation (AIQ Tool):** Custom Python tool using Jena/RDF4J (for OWL/SHACL reasoning against a domain ontology) and potentially custom logic to refine LLM output, ensure consistency, and generate LTL/CTL annotations for formal properties.
        *   **SMPC Coordination (AIQ Tool/Service):** If synthesis involves private data from multiple parties, an SMPC protocol (e.g., based on SPDZ) is orchestrated to compute parts of the P-IR without revealing raw inputs.
        *   **P-IR Graph Construction (AIQ Tool):** Writes the validated and refined P-IR (with LTL, version info) to the Neo4j P-IR Graph DB.
    *   **Technologies:** AIQ Toolkit, Quantized LLMs (Llama/Grok), Jena/RDF4J/SHACL, Python, SMPC libraries, Kafka (for results/status).
*   **3.1.3. P-IR Graph Database (Neo4j):**
    *   **Responsibilities:** Stores all versions of P-IRs as a graph. Nodes represent P-IR versions, clauses, source regulations, LTL properties, etc. Relationships define derivation, precedence, version history, and links to formal verification results. Enables complex querying for P-IR impact analysis, RGE policy selection, and audit.
    *   **Technologies:** Neo4j, Cypher, P-IR v2.0 schema mapped to graph properties.

#### 3.2. Echelon 2: Edge Governance Compilation & Enforcement
*   **3.2.1. Inference Gateway:**
    *   **Responsibilities:** Secure external API endpoint for client applications. Caches frequently accessed P-IR subsets (from Neo4j via Akamai or internal cache). Performs anomaly detection on incoming requests (Isolation Forest). Orchestrates calls to Edge RGE. Terminates PQC for external APIs (CRYSTALS-Kyber). Manages asynchronous tasks with Celery/Redis for complex pre/post-processing if needed.
    *   **Technologies:** FastAPI/Python, Celery, Redis, Akamai (or Varnish/Nginx cache), Scikit-learn (Isolation Forest), liboqs integration.
*   **3.2.2. Wasm RGE (Runtime Governance Engine):**
    *   **Responsibilities:** Deployed to serverless edge locations (AWS Lambda@Edge, Cloudflare Workers) or edge K8s. Executes P-IR logic with sub-millisecond latency.
        *   Receives context and P-IR reference from Inference Gateway.
        *   Loads/interprets relevant P-IR data (potentially HE encrypted parts).
        *   Uses DistilBERT (quantized ONNX/TensorRT) for semantic precedence between conflicting P-IR clauses.
        *   Parses and (partially, if feasible at edge) evaluates LTL/CTL conditions against runtime context.
        *   Performs HE operations (using SEAL/PALISADE wrappers) on encrypted P-IR fields.
        *   Compiles the final AI Constitution (system prompt) and governance decision.
    *   **Technologies:** Rust/C++ compiled to Wasm, Wasmtime/WasmEdge runtime, ONNX Runtime/TensorRT for DistilBERT (if Wasm supports GPU/NPU access or via host calls), HE library bindings.
*   **3.2.3. Application LLM Interface:** The Inference Gateway proxies requests to the target Application LLM, prepending the AI Constitution.
*   **3.2.4. AI Constitution Registry (OCI-Compliant):**
    *   **Responsibilities:** Stores versioned, signed Wasm RGE modules (which are essentially pre-compiled AI Constitutions or RGE configurations specific to a set of P-IRs). Edge Orchestrator pulls updates from here.
    *   **Technologies:** OCI-compliant registry (e.g., Harbor, Docker Hub, ECR).

#### 3.3. Echelon 3: Immutable Audit & Verification
*   **3.3.1. AuditKit (Hyperledger Fabric):**
    *   **Responsibilities:** Provides a tamper-proof, distributed ledger for all critical governance events (P-IR changes, RGE evaluations, FV results, access controls). Events are PQC-signed by their originating component. Offers CLI/UI for auditors and regulators. Supports audit replay.
    *   **Technologies:** Hyperledger Fabric, Go/Node.js (Chaincode), PQC library for signing.
*   **3.3.2. Formal Verification Module (NuSMV Wrapper):**
    *   **Responsibilities:** Receives P-IR clauses with LTL/CTL annotations from P-IR Management/Flink. Translates them into NuSMV (.smv) model files. Invokes NuSMV to check properties. Reports verification status (VERIFIED, FALSIFIED with counterexample) back to Neo4j and AuditKit.
    *   **Technologies:** Python wrapper, NuSMV (or TLA+), LTL/CTL parsing libraries.

#### 3.4. Cross-Cutting Components
*   **3.4.1. Cryptographic Services:** Libraries/modules providing PQC (liboqs), HE (SEAL/PALISADE), and SMPC functionalities, integrated into relevant services. A dedicated Key Management Service (KMS), possibly integrating with Vault, manages the lifecycle of PQC/HE keys.
*   **3.4.2. Quantum Optimization Interface (D-Wave Leap API):** Python scripts/service to formulate P-IR optimization problems (e.g., clause selection under resource constraints) as QUBOs and submit them to D-Wave Leap for prototyping.
*   **3.4.3. Monitoring & Observability Stack:** Prometheus for metrics, Grafana for dashboards, OpenTelemetry for distributed tracing (especially within AIQ Toolkit workflows for PGS-AI).
*   **3.4.4. Identity Management (SPIFFE/SPIRE):** For strong, attestable service identities in a Zero-Trust environment, particularly for Wasm RGE instances at the edge. Complements user/API IAM.

*(The document would continue with sections 4-11, elaborating on data flows, specific data models for Neo4j/Fabric, detailed security measures for PQC/HE/SMPC, scalability targets for each echelon, K8s/Serverless deployment specifics, AIQ Toolkit integration patterns, and the quantum roadmap based on ACGS-PGP Spec v2.0.)*

---

## 3. ACGS-PGP: Platform-Wide API Design Guidelines (OpenAPI)

**Document Version:** 2.0 (Aligning with Regulith Command Cycle 2.0)
**Date:** May 15, 2025
**Status:** DRAFT (Derived from ACGS-PGP Spec v2.0 Sec 4.0)

**Table of Contents:** (Extending previous TOC with Spec v2.0 details)

1.  **Introduction**
    1.1. Purpose
    1.2. Scope (All ACGS-PGP APIs: REST, gRPC, GraphQL; Internal & External)
    1.3. Audience
    1.4. Guiding Principles (Consistency, Security by Design (PQC), Performance, Discoverability)
    1.5. Specification Versions (OpenAPI 3.x, gRPC Proto3, GraphQL Schema Definition Language)
2.  **API Design Philosophy**
    2.1. Protocol Selection Rationale (REST for external/management, gRPC for internal low-latency, GraphQL for Neo4j flexible queries)
    2.2. Design-First Approach
3.  **URL Structure and Naming Conventions (REST/GraphQL)**
    3.1. Base Path (e.g., `/acgs/api/{version}/{service-name}/`)
    3.2. Resource Naming (Plural, kebab-case)
    3.3. Versioning (URI for REST, potentially headers/schema evolution for GraphQL/gRPC)
4.  **HTTP Methods (REST) & gRPC Method Types & GraphQL Operations**
5.  **Request/Response Structure**
    5.1. Headers (Standard + `X-PQC-Signature-Alg`, `X-PQC-Signature`, `X-HE-Scheme-ID`)
    5.2. Body (JSON for REST/GraphQL, Protobuf for gRPC)
    5.3. Status Codes (HTTP) & gRPC Status Codes
    5.4. Standard Error Response Format (including PQC/HE error codes)
6.  **Data Types and Formats (including PQC/HE data representation)**
7.  **Pagination, Filtering, Sorting (GraphQL & REST)**
8.  **Security for APIs (ACGS-PGP Spec v2.0 Sec 4.2, 4.3)**
    8.1. **Authentication:**
        *   External APIs (Inference Gateway): CRYSTALS-Kyber for KEM in TLS handshake, followed by JWT (PQC-signed if feasible) for application-level auth.
        *   Internal APIs (gRPC/REST): mTLS with PQC certificates (using SPIFFE/SPIRE identities) or PQC-signed JWTs.
    8.2. **Authorization:** RBAC enforced by API Gateway and individual services.
    8.3. **Data Integrity & Confidentiality:**
        *   PQC Signatures for critical messages/P-IRs.
        *   HE for specific sensitive fields in API payloads (clearly documented in OAS/Proto).
    8.4. Input Validation (against schemas, including cryptographic material format).
9.  **OpenAPI (for REST) / gRPC Proto / GraphQL Schema Best Practices**
    9.1. Clear definitions for PQC/HE related fields and security schemes.
10. **API Lifecycle Management (including PQC key rotation impact)**

---
*(Content for API Design Guidelines would elaborate on each point, focusing on how PQC, HE, and the different API styles (REST, gRPC, GraphQL) are consistently handled across the platform as per ACGS-PGP Spec v2.0 Sec 4.0.)*

**Example OpenAPI Security Scheme for PQC KEM + JWT:**

```yaml
# In components.securitySchemes of an OpenAPI document
components:
  securitySchemes:
    PQC_KEM_JWT:
      type: apiKey # This is a conceptual representation; actual flow is more complex
      in: header # The JWT is in the header
      name: Authorization
      description: |
        Authentication uses a two-fold approach for enhanced security:
        1. Initial connection establishment MAY be protected by a TLS layer incorporating a 
           Post-Quantum Cryptography Key Encapsulation Mechanism (PQC KEM) like CRYSTALS-Kyber.
           This secures the channel over which the JWT is then passed.
        2. The `Authorization` header carries a Bearer token (JWT). This JWT itself MIGHT be
           signed with a PQC algorithm if supported by the IAM service and client.
        The `scheme` is 'bearer', `bearerFormat` is 'JWT'. The PQC aspect primarily applies
        to the secure channel establishment or the JWT signature algorithm itself, which is
        validated by the server. Refer to ACGS-PGP security documentation for details on
        PQC algorithm negotiation and JWT validation.
    # Standard JWT Bearer for cases where PQC KEM is handled at TLS layer only
    # and JWT uses conventional signatures, or for internal JWTs.
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

**Example gRPC Proto with PQC/HE consideration:**

```protobuf
// In rge_internal_service.proto
message EncryptedPIRField {
    string field_path = 1; // JSONPath to the original field
    bytes he_ciphertext = 2;
    string he_scheme_id = 3;
    bytes pqc_kem_public_key_id_for_response_encryption = 4; // If RGE needs to re-encrypt for a specific recipient
}

message PIRContextRequest {
    // ... other fields ...
    repeated EncryptedPIRField encrypted_pir_trigger_values = 10;
}
```

---

## 4. ACGS-PGP: Security Architecture & Design Document

**Document Version:** 2.0 (Aligning with Regulith Command Cycle 2.0)
**Date:** May 15, 2025
**Status:** DRAFT (Derived from ACGS-PGP Spec v2.0 Sec 4.0, 5.0)

**Table of Contents:** (Extending previous TOC with Spec v2.0 details)

1.  **Introduction**
    1.1. Purpose (Detailing security for Command Layer)
    1.2. Scope (PQC, HE, SMPC, DLT security, Wasm RGE security, AIQ security)
    1.3. Audience
    1.4. Security Guiding Principles (Zero-Trust Command, Quantum-Resistance, Verifiable Integrity, Confidential Computing) [ACGS-PGP Spec v2.0 Sec 5.1]
2.  **Threat Model & Risk Assessment (for Advanced Components)**
    2.1. Threats to PQC Key Management & Exchange (e.g., side-channel on KEM, implementation bugs in liboqs).
    2.2. Threats to HE Schemes (e.g., chosen ciphertext attacks if scheme is not CCA2, parameter misuse, oracle attacks on RGE HE module).
    2.3. Threats to SMPC Protocols (e.g., collusion, malicious participants, input privacy leakage).
    2.4. Threats to DLT (AuditKit) (e.g., 51% attack on ordering service (if applicable to Fabric setup), chaincode vulnerabilities, private key compromise of peers/endorsers).
    2.5. Threats to Wasm RGE (e.g., Wasm sandbox escape, side-channels in Wasm runtime, vulnerabilities in host function interface, insecure DistilBERT model loading).
    2.6. Threats to Formal Verification Module (e.g., incorrect P-IR to SMV translation, NuSMV vulnerabilities).
    2.7. Threats to AIQ Toolkit & PGS-AI Workflow (e.g., compromised AIQ tool, data poisoning in fine-tuning Llama/Grok, adversarial inputs to symbolic engine).
3.  **Identity and Access Management (IAM) - Zero Trust Command**
    3.1. **Service Identity (SPIFFE/SPIRE):** Cryptographically verifiable identities for all microservices, Wasm RGE instances, and AIQ tools. SVIDs used for mTLS.
    3.2. **User Authentication:** PQC-augmented user authentication flows (e.g., PQC for password hashing storage, or PQC in FIDO2 keys).
    3.3. **Authorization:** Fine-grained RBAC/ABAC, with critical policies potentially managed as P-IRs themselves and enforced by a meta-RGE. Smart contracts on AuditKit for managing high-privilege role assignments.
4.  **Cryptographic Primitives & Key Management (ACGS-PGP Spec v2.0 Sec 4.3)**
    4.1. **Post-Quantum Cryptography (PQC):**
        *   KEMs: CRYSTALS-Kyber for TLS key exchange and secure data encapsulation (via liboqs).
        *   Signatures: CRYSTALS-Dilithium/Falcon for P-IR integrity, AuditKit event signing, Wasm module signing.
        *   PQC Certificate Authority & PKI strategy.
        *   Key Rotation & Revocation for PQC keys.
    4.2. **Homomorphic Encryption (HE):**
        *   Schemes: Microsoft SEAL / PALISADE (BFV/BGV for exact computations on integers, CKKS for approximate on reals).
        *   HE Parameter Selection & Management (tied to `heSchemeId` in P-IR).
        *   HE Key Generation, Distribution, Storage (via KMS/Vault, potentially using PQC KEM to protect HE keys).
        *   Secure HE computation in Wasm RGE (noise management, circuit privacy considerations).
    4.3. **Secure Multi-Party Computation (SMPC):**
        *   Protocols: SPDZ, GMW, or similar for specific PGS-AI synthesis tasks.
        *   Participant Onboarding & Identity.
        *   Secure Input Provisioning & Output Reconstruction.
        *   Randomness Generation.
    4.4. **Key Management Service (KMS):** Centralized service (integrating with Vault) for managing lifecycle of PQC, HE keys. HSMs for root keys.
5.  **Data Security (with Advanced Crypto)**
    5.1. P-IR Security: PQC signatures for integrity. HE for sensitive fields during RGE processing.
    5.2. AuditKit Security: PQC signatures on all Fabric transactions. Immutability of the DLT. Access control to query API.
    5.3. Secure Data Streams (Kafka with PQC-TLS).
6.  **Wasm RGE Security**
    6.1. Wasm Runtime Hardening (e.g., Wasmtime/WasmEdge security features).
    6.2. Secure Host Function Interface (least privilege for Wasm module).
    6.3. Input Sanitization for context passed to Wasm.
    6.4. Resource Constraints for Wasm execution (CPU, memory).
    6.5. Secure Loading and Verification of Wasm AI Constitution Modules (PQC-signed from OCI Registry).
7.  **AIQ Toolkit Security (for PGS-AI)**
    7.1. Secure execution environment for AIQ tools.
    7.2. Input/output validation for each tool in the workflow.
    7.3. RBAC for accessing/executing AIQ workflows.
    7.4. Secure handling of secrets (e.g., LLM API keys, Neo4j creds) by AIQ via Vault.
8.  **Formal Verification Security**
    8.1. Ensuring integrity of P-IR to SMV translation.
    8.2. Secure environment for NuSMV execution.
    8.3. Authenticity of verification results reported to Neo4j/AuditKit.
9.  **Quantum Optimization Security (D-Wave Interface)**
    9.1. Secure API communication with D-Wave Leap.
    9.2. Ensuring QUBO formulation does not leak sensitive P-IR data.
10. **Incident Response for Advanced Threats**
    10.1. Procedures for PQC key compromise, HE scheme break, SMPC collusion detection.
    10.2. Responding to Wasm RGE exploits.

---
*(Content for Security Architecture Document would continue, detailing specific controls, protocols, and procedures for each advanced technology based on ACGS-PGP Spec v2.0.)*

---

## 5. ACGS-PGP: Comprehensive Testing Strategy Document

**Document Version:** 2.0 (Aligning with Regulith Command Cycle 2.0)
**Date:** May 15, 2025
**Status:** DRAFT (Derived from ACGS-PGP Spec v2.0 Sec 6.0, 7.0)

**Table of Contents:** (Extending previous TOC with Spec v2.0 details)

1.  **Introduction**
    1.1. Purpose (Ensuring quality of Command Layer)
    1.2. Scope (All components, including PQC, HE, SMPC, DLT, Wasm RGE, FV, AIQ)
    1.3. Audience
    1.4. Testing Philosophy (Continuous, Automated, Risk-Driven, "Verify by Design")
2.  **Testing Levels and Types (Elaborated)**
    2.1. Unit Testing (Rust/C++ for RGE, Go/Node for Chaincode, Python for services/AIQ tools)
    2.2. Integration Testing (Service-to-DLT, Service-to-KMS, Wasm-Host, AIQ Tool-to-Tool)
    2.3. API Contract Testing (gRPC, GraphQL, REST with PQC/HE considerations)
    2.4. System/E2E Testing (Complex scenarios involving all Echelons)
    2.5. Performance Testing (Sub-ms RGE, High-throughput Gateway, DLT tps, Flink job latency)
    2.6. **Security Testing (Focus on Advanced Crypto & Components):**
        *   PQC Implementation Testing (Side-channel resistance tests for liboqs usage, KEM/Sig correctness).
        *   HE Scheme Testing (Correctness of HE operations, noise analysis, vulnerability to known HE attacks).
        *   SMPC Protocol Testing (Security against defined adversary models, correctness of computation).
        *   Wasm RGE Fuzzing & Sandbox Escape Testing.
        *   Chaincode Security Audits for AuditKit.
        *   Penetration Testing targeting PQC/HE/SMPC integrations.
    2.7. Resilience Testing (Chaos engineering for DLT nodes, Kafka/Flink, Edge RGEs)
3.  **AI Governance Specific Testing (Command Layer Focus)**
    3.1. **P-IR v2.0 Schema Validation & Integrity:** (Neo4j SHACL validation for graph properties).
    3.2. **Wasm RGE Policy Enforcement Testing:**
        *   Testing LTL/CTL evaluation logic within RGE.
        *   Testing HE-based trigger condition evaluation.
        *   Testing DistilBERT precedence logic.
        *   Validation of AI Constitution Wasm module compilation and execution.
    3.3. **Hybrid PGS-AI (AIQ Workflow) Output Quality Testing:**
        *   Accuracy of LTL/CTL annotation generation.
        *   Correctness of P-IR to Neo4j graph mapping.
        *   Effectiveness of SMPC stubs in AIQ workflow.
        *   End-to-end P-IR synthesis quality from `NormalizedRegulationEvent`.
    3.4. **Formal Verification Module Testing:**
        *   Correctness of P-IR clause to NuSMV model translation.
        *   Accuracy of NuSMV result interpretation.
        *   Scalability for verifying large sets of P-IR properties.
    3.5. **AuditKit Testing:**
        *   Integrity and non-repudiation of logged events (PQC signature verification).
        *   Correctness of chaincode logic for asset creation and querying.
        *   Performance of AuditKit query layer.
    3.6. **Quantum Optimization (D-Wave) Prototype Testing:**
        *   Correctness of QUBO formulation from P-IR hints.
        *   Feasibility of achieving meaningful optimization results.
4.  **Test Environments (Including Edge & DLT Staging)**
5.  **Test Automation Strategy (for Advanced Components)**
    5.1. Specialized frameworks for testing Wasm, chaincode, crypto modules.
    5.2. AIQ Toolkit's evaluation capabilities for PGS-AI workflows.
6.  **Defect Management for Complex Failures**
7.  **Roles and Responsibilities (Specialized Testers for Crypto, DLT, FV)**

---
*(Content for Testing Strategy would elaborate on methodologies for each advanced component, specific metrics for PQC success rates, HE noise levels, SMPC correctness, FV coverage, DLT transaction integrity, etc., based on ACGS-PGP Spec v2.0.)*

---

## 6. ACGS-PGP: Synthesis LLM Design, Training, and Evaluation Document

**Document Version:** 2.0 (Aligning with Regulith Command Cycle 2.0 - Hybrid PGS-AI)
**Date:** May 15, 2025
**Status:** DRAFT (Derived from ACGS-PGP Spec v2.0 Sec 3.2.1, AIQ Integration)

**Table of Contents:** (Extending previous TOC with Spec v2.0 details)

1.  **Introduction**
    1.1. Purpose (Design of Hybrid PGS-AI for P-IR v2.0 generation)
    1.2. Role of Hybrid PGS-AI (Llama/Grok + Symbolic + SMPC via AIQ)
    1.3. Key Objectives (Accuracy, Schema v2.0 Adherence, LTL/CTL Annotation, HE/PQC field population hints)
2.  **Hybrid PGS-AI Architecture (AIQ Toolkit Based)**
    2.1. **AIQ Workflow (`pgs_ai_hybrid_synthesis_v2.yaml`):**
        *   Input: `NormalizedRegulationEvent`, Target P-IR v2.0 Schema, AI Constitution context.
        *   Task 1: LLM Intent & Structure Extraction (Llama/Grok NIM via AIQ Tool) - Outputs draft P-IR fields, potential LTL intents.
        *   Task 2: Symbolic Refinement & Validation (Jena/RDF4J/SHACL via AIQ Tool) - Validates against domain ontology, P-IR schema, refines structure.
        *   Task 3: LTL/CTL Annotation Generation (AIQ Tool with LTL library/heuristics) - Generates formal properties based on refined structure and deontic cues.
        *   Task 4: Cryptographic Policy Hinting (AIQ Tool) - Suggests `homomorphicEncryptionPolicy` fields or `pqcSignature` requirements based on data sensitivity tags in input or ontology.
        *   Task 5 (Optional, if SMPC needed): SMPC Sub-Workflow Invocation (AIQ Tool orchestrating SMPC).
        *   Task 6: P-IR v2.0 Assembly & Neo4j Graph Construction (AIQ Tool).
    2.2. Base LLM Models (Llama/Grok, 4-bit quantized) - Fine-tuning strategy.
    2.3. Symbolic AI Component (Ontology: P-IR concepts, regulatory domains; Rules: SHACL for P-IR v2.0, custom rules for LTL generation).
    2.4. AIQ Toolkit Custom Tools (Python wrappers for LLM, Jena, LTL lib, SMPC stubs, Neo4j client).
3.  **Data Strategy for Hybrid PGS-AI**
    3.1. Training Data for LLM Fine-Tuning (Intent -> Draft P-IR v2.0 fields, Intent -> LTL intents).
    3.2. Knowledge Base for Symbolic AI (Domain ontologies, regulatory knowledge graphs).
    3.3. Data for SMPC simulation/testing.
4.  **Prompt Engineering for Hybrid Interaction**
    4.1. Prompts for LLM to output structured data compatible with symbolic refinement.
    4.2. Prompts for LTL intent extraction.
5.  **AIQ Toolkit Implementation Details**
    5.1. Configuration of AIQ tools, parameters, secrets management.
    5.2. Error handling and retry logic within the AIQ workflow.
    5.3. Observability (metrics, logs, traces) via AIQ.
6.  **Evaluation Strategy for Hybrid PGS-AI**
    6.1. P-IR v2.0 Output Quality (Schema Adherence, Accuracy of all fields including LTL, HE/PQC hints).
    6.2. Correctness of LTL/CTL annotations (against expert-defined properties).
    6.3. Effectiveness of Symbolic Refinement (consistency, constraint satisfaction).
    6.4. Performance of the end-to-end AIQ workflow.
    6.5. Robustness against adversarial inputs to the workflow.
7.  **Governance of the Hybrid PGS-AI**
    7.1. Versioning of AIQ workflows, tools, models, ontologies.
    7.2. Human oversight and validation of synthesized P-IRs v2.0.

---
*(Content for Synthesis LLM Document would detail the AIQ workflow, the prompts for Llama/Grok, the OWL/SHACL rules for the symbolic component, how LTL annotations are generated, and how hints for HE/PQC fields are derived based on ACGS-PGP Spec v2.0.)*

---

## 7. ACGS-PGP: Microservice Design Document (SDD) Template

**(This remains a template, as provided before. It will be applied to each microservice detailed in ACGS-PGP Spec v2.0, such as the refined Wasm RGE, the Neo4j P-IR Management Service, the Fabric AuditKit Service, the Formal Verification Module Service, the Inference Gateway, etc.)**

**Service Name:** `[Name of the Microservice - e.g., Wasm RGE Service]`
**Document Version:** 2.0 (Aligning with Regulith Command Cycle 2.0)
**Date:** `[Date of Last Update]`
**Status:** `[DRAFT | IN REVIEW | APPROVED | DEPRECATED]`
**Lead Developer(s)/Architect(s):** `[Names/Team]`

**Table of Contents:** (Adjusted for advanced components)

1.  **Introduction**
    1.1. Purpose of this Document
    1.2. Service Overview and Core Responsibilities (as per ACGS-PGP Spec v2.0 Sec 3.2)
    1.3. Key Features / Functionalities (e.g., for RGE: Wasm execution, HE processing, LTL parsing, DistilBERT precedence)
    1.4. Relationship to Other Services and Echelons
2.  **Service Architecture & Design**
    2.1. High-Level Component Diagram (Internal components, e.g., RGE: Wasm Runtime, HE Module, LTL Parser, NLP Model Interface)
    2.2. Key Technologies (Rust/C++ for Wasm, liboqs, SEAL/PALISADE, ONNX Runtime, specific DLT SDKs, AIQ client libs)
    2.3. Core Logic and Algorithms (Detailed, e.g., RGE's P-IR graph traversal, HE computation flow, LTL evaluation steps, SMPC protocol interaction for PGS-AI tools)
3.  **API Specification (gRPC, REST, GraphQL as applicable)**
    3.1. Link to .proto / OpenAPI / GraphQL Schema File
    3.2. Summary of Key Methods/Endpoints (including PQC/HE parameters)
4.  **Data Model and Persistence (if applicable, e.g., Neo4j service, Fabric Chaincode state)**
5.  **Inter-Component Communication & Dependencies (within ACGS-PGP Echelons)**
    5.1. APIs Consumed (e.g., RGE consuming P-IRs from Neo4j via GraphQL, KMS for HE keys)
    5.2. Events Produced/Consumed (Kafka, with PQC-signed payloads where specified)
6.  **Scalability and Performance (Targets from ACGS-PGP Spec v2.0 KSOs)**
    6.1. Specifics for Wasm edge scaling, DLT tps, Flink job parallelism.
7.  **Resilience and Error Handling (for advanced components)**
    7.1. Handling failures in PQC/HE operations, DLT consensus, FV timeouts.
8.  **Security Considerations (Service-Specific for PQC, HE, SMPC, DLT, Wasm)**
    8.1. Secure Wasm execution, HE key handling, PQC library usage, chaincode security.
9.  **Configuration Management (including crypto parameters, DLT peer addresses)**
10. **Deployment (Kubernetes, Serverless Edge, DLT Network Setup)**
11. **Logging and Monitoring (including crypto operation success/failure, DLT transaction metrics, FV progress)**
12. **Testing Strategy (Service-Specific for advanced features)**
    12.1. Unit tests for crypto operations, Wasm modules, chaincode logic.
    12.2. Integration tests with KMS, DLT network, NuSMV.
13. **Future Considerations / Known Limitations**

---

## Summaries for Remaining Documents

**8. ACGS-PGP: Coding Standards & Best Practices (Multi-Language)**
*   **Intended Content:** Building on the previous outline, this would now include specific standards for Rust/C++ (for Wasm RGE), Go/Node.js (for Fabric Chaincode), Python (for services, AIQ tools, FV/D-Wave wrappers), and potentially Java/Scala (for Flink jobs). It would cover secure coding for cryptographic operations (PQC, HE, SMPC), Wasm development best practices, chaincode development guidelines, and AIQ tool development standards. Emphasis on memory safety for Rust/C++, secure use of crypto libraries, and robust error handling in distributed systems.

**9. ACGS-PGP: CI/CD Pipeline Design & Developer Guide (for Advanced Artifacts)**
*   **Intended Content:** Expands on the previous outline to detail CI/CD stages for:
    *   **Wasm RGE Modules:** Compilation, optimization, testing in Wasm runtimes, signing, publishing to OCI Constitution Registry.
    *   **Hybrid PGS-AI (AIQ Workflows & Models):** Testing AIQ tools, packaging AIQ workflows, versioning fine-tuned LLMs (Git LFS for checkpoints), building/pushing PGS-AI service Docker images.
    *   **Hyperledger Fabric Chaincode:** Linting, unit testing, packaging, and automated deployment/upgrade scripts for chaincode on dev/staging Fabric networks.
    *   **Flink Jobs:** Compilation, unit testing, packaging, and deployment to Flink cluster.
    *   **Formal Verification Models:** Automated P-IR to SMV translation tests, integration with NuSMV execution in CI as a gate.
    *   **Cryptographic Modules:** Rigorous testing and validation for any custom crypto wrappers.
    *   Deployment to diverse targets (K8s, Serverless Edge, DLT networks).

**10. ACGS-PGP: LLM Constitutional Alignment Verification Protocol (Command Layer)**
*   **Intended Content:** Focuses on verifying that the *entire ACGS-PGP Command Layer system* correctly implements and enforces the AI Constitution through the P-IRs and RGE logic. This involves:
    *   Mapping constitutional principles to specific P-IR v2.0 features (LTL annotations, trigger types, action types).
    *   Designing test scenarios where specific constitutional principles *should* lead to predictable RGE behavior (e.g., a "do no harm" principle translating to P-IRs that block harmful content, and the RGE correctly enforcing these).
    *   Validating that the PGS-AI correctly translates constitutional principles into P-IRs with appropriate LTL/formal properties.
    *   Using the Formal Verification Module's outputs as evidence of constitutional alignment for specific P-IR properties.
    *   Auditing (via AuditKit) that AI Constitutions compiled by the RGE are consistent with active, verified P-IRs.

**11. ACGS-PGP: Red Teaming Execution Plan (Targeting Command Layer)**
*   **Intended Content:** Specific red teaming scenarios for the advanced components:
    *   **PQC/HE/SMPC:** Attempting to break/bypass cryptographic protections (e.g., side-channel attacks on PQC implementations if custom, oracle attacks on HE if RGE exposes exploitable behavior, collusion simulation for SMPC).
    *   **Wasm RGE:** Fuzzing Wasm inputs, attempting sandbox escapes, exploiting vulnerabilities in the Wasm runtime or host function interface.
    *   **DLT (AuditKit):** Attempting to tamper with Fabric ledger (if misconfigured), exploiting chaincode vulnerabilities, unauthorized access to audit query API.
    *   **Formal Verification Bypass:** Crafting P-IRs with subtle flaws that pass FV but still lead to undesirable RGE behavior, or attacking the P-IR-to-SMV translation.
    *   **AIQ Workflow Exploitation:** Injecting malicious data into AIQ tool inputs, attempting to compromise the AIQ orchestrator.

**12. ACGS-PGP: Operational Guide (Command Layer Operations)**
*   **Intended Content:** Procedures for:
    *   Deploying and managing K8s clusters for Echelon 1 & 3.
    *   Deploying and managing Wasm RGEs on serverless edge platforms (including OCI registry integration).
    *   Operating and maintaining the Hyperledger Fabric network for AuditKit.
    *   Managing the Neo4j P-IR graph database (backups, scaling, schema migrations).
    *   Operating the Kafka/Flink data ingestion and P-IR processing pipeline.
    *   Managing the lifecycle of PQC and HE keys via the KMS.
    *   Monitoring the health and performance of all echelons and advanced components (PQC negotiation rates, HE computation times, SMPC protocol success, FV run times, DLT transaction throughput).
    *   Troubleshooting issues related to Wasm execution, crypto operations, DLT consensus, etc.

**13. ACGS-PGP: User Manual (for Advanced Platform Users)**
*   **Intended Content:** Guides for:
    *   **Governance Experts/Policy Authors:** Using the UI/API to define P-IRs with LTL/CTL annotations, specifying HE policies for sensitive fields, providing hints for quantum optimization. Understanding FV results.
    *   **AI Engineers (PGS-AI):** Using the AIQ Toolkit to develop, test, and deploy P-IR synthesis workflows. Managing domain ontologies for the symbolic AI component.
    *   **Security/Crypto Engineers:** Managing PQC/HE keys, configuring SMPC protocols, reviewing PQC signatures on P-IRs/AuditKit events.
    *   **Auditors/Regulators:** Using the AuditKit UI/CLI to query immutable logs, verify PQC signatures, review FV status of P-IRs.
    *   **Quantum Engineers (Prototype Phase):** Interacting with the D-Wave interface, interpreting optimization results for P-IRs.

This detailed population, based on your "Regulith Command Cycle 2.0" specification, should provide the necessary depth for the selected artifacts.
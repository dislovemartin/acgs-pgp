# Policy Service API Documentation

The Policy Service is responsible for managing policies (P-IRs) and AI Constitutions in the ACGS-PGP system.

## Base URL

```
http://localhost:8000/api/v1
```

## Policies API

### List Policies

Retrieves a list of policies with optional filtering.

**Endpoint:** `GET /policies`

**Query Parameters:**

- `skip` (integer, optional): Number of records to skip for pagination. Default: 0.
- `limit` (integer, optional): Maximum number of records to return. Default: 100.
- `status` (string, optional): Filter by policy status. Values: "draft", "active", "deprecated", "archived".
- `severity` (string, optional): Filter by policy severity. Values: "low", "medium", "high", "critical".
- `min_priority` (integer, optional): Filter by minimum priority value (0-100).
- `tags` (array of strings, optional): Filter by tags.
- `constitutional_references` (array of strings, optional): Filter by constitutional references.

**Response:**

```json
[
  {
    "policy_id": "550e8400-e29b-41d4-a716-446655440000",
    "version": 1,
    "name": "Prevent PII Disclosure",
    "description": "Prevents sharing of personally identifiable information",
    "status": "active",
    "constitutional_references": ["privacy.1", "security.3"],
    "scope": {
      "llm_models_inclusion": "all",
      "llm_models_list": [],
      "user_roles_inclusion": "all",
      "user_roles_list": [],
      "applications_inclusion": "all",
      "applications_list": [],
      "data_sensitivity_inclusion": "minimum",
      "data_sensitivity_levels": ["public", "internal", "confidential", "restricted"]
    },
    "trigger_conditions": {
      "prompt_patterns": [
        {
          "pattern": "social security",
          "is_regex": false,
          "case_sensitive": false,
          "description": "Match SSN mentions"
        },
        {
          "pattern": "\\d{3}-\\d{2}-\\d{4}",
          "is_regex": true,
          "case_sensitive": false,
          "description": "Match SSN format"
        }
      ],
      "context_attributes": [],
      "tool_usage_requests": [],
      "response_patterns": [],
      "custom_conditions": [],
      "condition_logic": "ANY"
    },
    "governance_actions": [
      {
        "action_type": "block_execution",
        "parameters": {
          "message": "This prompt contains potentially sensitive PII and cannot be processed."
        },
        "priority": 100,
        "description": "Block execution when PII is detected"
      }
    ],
    "severity": "high",
    "priority": 80,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "created_by": "system@acgs-pgp.local",
    "updated_by": "system@acgs-pgp.local",
    "tags": ["security", "compliance", "pii"],
    "metadata": {
      "author": "compliance-team",
      "created_timestamp": "2023-01-01T00:00:00Z",
      "last_updated_timestamp": "2023-01-01T00:00:00Z",
      "approval_history": [
        {
          "approved_by": "compliance-officer",
          "approved_at": "2023-01-01T12:00:00Z",
          "comments": "Approved after review"
        }
      ],
      "synthesis_details": {
        "synthesized_by": "gpt-4",
        "synthesized_at": "2023-01-01T00:00:00Z",
        "source_type": "llm",
        "source_details": {
          "prompt": "Create a policy to prevent PII disclosure"
        },
        "confidence_score": 0.95
      },
      "compliance_standards": ["GDPR", "CCPA"],
      "custom_metadata": {
        "business_unit": "customer_service"
      }
    }
  }
]
```

### Get Policy

Retrieves a specific policy by ID.

**Endpoint:** `GET /policies/{policy_id}`

**Path Parameters:**

- `policy_id` (string, required): The ID of the policy to retrieve.

**Response:**

Same as the policy object in the List Policies response.

### Create Policy

Creates a new policy.

**Endpoint:** `POST /policies`

**Request Body:**

```json
{
  "name": "Prevent PII Disclosure",
  "description": "Prevents sharing of personally identifiable information",
  "status": "draft",
  "constitutional_references": ["privacy.1", "security.3"],
  "scope": {
    "llm_models_inclusion": "all",
    "llm_models_list": [],
    "user_roles_inclusion": "all",
    "user_roles_list": [],
    "applications_inclusion": "all",
    "applications_list": [],
    "data_sensitivity_inclusion": "minimum",
    "data_sensitivity_levels": ["public", "internal", "confidential", "restricted"]
  },
  "trigger_conditions": {
    "prompt_patterns": [
      {
        "pattern": "social security",
        "is_regex": false,
        "case_sensitive": false,
        "description": "Match SSN mentions"
      }
    ],
    "condition_logic": "ANY"
  },
  "governance_actions": [
    {
      "action_type": "block_execution",
      "parameters": {
        "message": "This prompt contains potentially sensitive PII and cannot be processed."
      },
      "priority": 100,
      "description": "Block execution when PII is detected"
    }
  ],
  "severity": "high",
  "priority": 80,
  "tags": ["security", "compliance", "pii"],
  "created_by": "system@acgs-pgp.local",
  "updated_by": "system@acgs-pgp.local"
}
```

**Response:**

Same as the policy object in the List Policies response.

### Update Policy

Updates an existing policy.

**Endpoint:** `PUT /policies/{policy_id}`

**Path Parameters:**

- `policy_id` (string, required): The ID of the policy to update.

**Request Body:**

```json
{
  "name": "Updated Policy Name",
  "description": "Updated description",
  "status": "active",
  "severity": "critical",
  "priority": 90,
  "updated_by": "admin@acgs-pgp.local"
}
```

**Response:**

Same as the policy object in the List Policies response.

### Delete Policy

Deletes a policy.

**Endpoint:** `DELETE /policies/{policy_id}`

**Path Parameters:**

- `policy_id` (string, required): The ID of the policy to delete.

**Response:**

```json
{
  "ok": true
}
```

## AI Constitution API

### List Constitutions

Retrieves a list of AI Constitutions.

**Endpoint:** `GET /constitution`

**Query Parameters:**

- `skip` (integer, optional): Number of records to skip for pagination. Default: 0.
- `limit` (integer, optional): Maximum number of records to return. Default: 100.

**Response:**

```json
[
  {
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
]
```

### Get Latest Constitution

Retrieves the latest version of the AI Constitution.

**Endpoint:** `GET /constitution/latest`

**Response:**

Same as the constitution object in the List Constitutions response.

### Get Constitution

Retrieves a specific AI Constitution by ID.

**Endpoint:** `GET /constitution/{constitution_id}`

**Path Parameters:**

- `constitution_id` (string, required): The ID of the constitution to retrieve.

**Response:**

Same as the constitution object in the List Constitutions response.

### Create Constitution

Creates a new AI Constitution.

**Endpoint:** `POST /constitution`

**Request Body:**

```json
{
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
    }
  ],
  "categories": ["privacy", "fairness", "transparency", "security", "accountability"],
  "created_by": "system@acgs-pgp.local",
  "updated_by": "system@acgs-pgp.local",
  "metadata": {
    "version_notes": "Initial version",
    "approved_by": "ethics_board",
    "approval_date": "2023-01-01T00:00:00Z"
  }
}
```

**Response:**

Same as the constitution object in the List Constitutions response.

### Update Constitution

Updates an existing AI Constitution.

**Endpoint:** `PUT /constitution/{constitution_id}`

**Path Parameters:**

- `constitution_id` (string, required): The ID of the constitution to update.

**Request Body:**

```json
{
  "title": "Updated AI Constitution",
  "description": "Updated description",
  "updated_by": "admin@acgs-pgp.local"
}
```

**Response:**

Same as the constitution object in the List Constitutions response.

### Delete Constitution

Deletes an AI Constitution.

**Endpoint:** `DELETE /constitution/{constitution_id}`

**Path Parameters:**

- `constitution_id` (string, required): The ID of the constitution to delete.

**Response:**

```json
{
  "ok": true
}
```

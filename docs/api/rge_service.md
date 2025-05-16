# RGE Service API Documentation

The Runtime Governance Engine (RGE) Service is responsible for evaluating policies against prompts and applying governance actions.

## Base URL

```
http://localhost:8001/api/v1
```

## Evaluate API

### Evaluate Policies

Evaluates a prompt against the active policies and returns the applicable governance actions.

**Endpoint:** `POST /evaluate`

**Request Body:**

```json
{
  "prompt": "This is a prompt that might contain sensitive information like a social security number 123-45-6789.",
  "metadata": {
    "model_name": "gpt-4",
    "user_role": "standard",
    "application": "customer-service",
    "data_sensitivity": "confidential",
    "tools_used": ["sensitive_data_tool"],
    "tool_parameters": {
      "sensitive_data_tool": {
        "access_level": "high"
      }
    },
    "response_text": "This is a sample response that might be analyzed."
  }
}
```

**Request Fields:**

- `prompt` (string, required): The prompt to evaluate.
- `metadata` (object, optional): Additional context for policy evaluation.
  - `model_name` (string, optional): The name of the LLM model being used.
  - `user_role` (string, optional): The role of the user making the request.
  - `application` (string, optional): The application making the request.
  - `data_sensitivity` (string, optional): The sensitivity level of the data.
  - `tools_used` (array of strings, optional): The tools being used in the request.
  - `tool_parameters` (object, optional): Parameters for the tools being used.
  - `response_text` (string, optional): The response text to evaluate (for response pattern matching).

**Response:**

```json
{
  "modified_prompt": "This is a prompt that might contain sensitive information like a [REDACTED].",
  "actions": [
    {
      "policy_id": "550e8400-e29b-41d4-a716-446655440000",
      "policy_name": "Prevent PII Disclosure",
      "action_type": "redact",
      "parameters": {
        "pattern": "\\d{3}-\\d{2}-\\d{4}",
        "replacement": "[REDACTED]"
      },
      "priority": 80,
      "description": "Redact SSNs from prompts"
    }
  ],
  "blocked": false,
  "requires_approval": false,
  "evaluation_time": "2023-01-01T00:00:00Z",
  "matched_policies": [
    {
      "policy_id": "550e8400-e29b-41d4-a716-446655440000",
      "policy_name": "Prevent PII Disclosure",
      "matched_conditions": [
        {
          "type": "prompt_pattern",
          "pattern": {
            "pattern": "\\d{3}-\\d{2}-\\d{4}",
            "is_regex": true,
            "case_sensitive": false,
            "description": "Match SSN format"
          }
        }
      ]
    }
  ]
}
```

**Response Fields:**

- `modified_prompt` (string): The prompt after applying any modifications from governance actions.
- `actions` (array of objects): The governance actions that were applied.
  - `policy_id` (string): The ID of the policy that triggered the action.
  - `policy_name` (string): The name of the policy that triggered the action.
  - `action_type` (string): The type of governance action.
  - `parameters` (object): The parameters for the action.
  - `priority` (integer): The priority of the action.
  - `description` (string): A description of the action.
- `blocked` (boolean): Whether the prompt was blocked by any policy.
- `requires_approval` (boolean): Whether the prompt requires approval.
- `evaluation_time` (string): The time when the evaluation was performed.
- `matched_policies` (array of objects): The policies that matched the prompt.
  - `policy_id` (string): The ID of the policy.
  - `policy_name` (string): The name of the policy.
  - `matched_conditions` (array of objects): The conditions that matched the prompt.
    - `type` (string): The type of condition that matched.
    - `pattern` (object): Details of the pattern that matched.

### Batch Evaluate Policies

Evaluates multiple prompts against the active policies in a single request.

**Endpoint:** `POST /evaluate/batch`

**Request Body:**

```json
{
  "prompts": [
    {
      "id": "prompt1",
      "text": "This is the first prompt to evaluate.",
      "metadata": {
        "model_name": "gpt-4",
        "user_role": "standard"
      }
    },
    {
      "id": "prompt2",
      "text": "This is the second prompt with a social security number 123-45-6789.",
      "metadata": {
        "model_name": "gpt-4",
        "user_role": "admin"
      }
    }
  ]
}
```

**Request Fields:**

- `prompts` (array of objects, required): The prompts to evaluate.
  - `id` (string, required): A unique identifier for the prompt.
  - `text` (string, required): The prompt text to evaluate.
  - `metadata` (object, optional): Additional context for policy evaluation.

**Response:**

```json
{
  "results": [
    {
      "id": "prompt1",
      "modified_prompt": "This is the first prompt to evaluate.",
      "actions": [],
      "blocked": false,
      "requires_approval": false,
      "matched_policies": []
    },
    {
      "id": "prompt2",
      "modified_prompt": "This is the second prompt with a social security number [REDACTED].",
      "actions": [
        {
          "policy_id": "550e8400-e29b-41d4-a716-446655440000",
          "policy_name": "Prevent PII Disclosure",
          "action_type": "redact",
          "parameters": {
            "pattern": "\\d{3}-\\d{2}-\\d{4}",
            "replacement": "[REDACTED]"
          },
          "priority": 80,
          "description": "Redact SSNs from prompts"
        }
      ],
      "blocked": false,
      "requires_approval": false,
      "matched_policies": [
        {
          "policy_id": "550e8400-e29b-41d4-a716-446655440000",
          "policy_name": "Prevent PII Disclosure",
          "matched_conditions": [
            {
              "type": "prompt_pattern",
              "pattern": {
                "pattern": "\\d{3}-\\d{2}-\\d{4}",
                "is_regex": true,
                "case_sensitive": false,
                "description": "Match SSN format"
              }
            }
          ]
        }
      ]
    }
  ],
  "evaluation_time": "2023-01-01T00:00:00Z"
}
```

**Response Fields:**

- `results` (array of objects): The evaluation results for each prompt.
  - `id` (string): The identifier of the prompt.
  - `modified_prompt` (string): The prompt after applying any modifications.
  - `actions` (array of objects): The governance actions that were applied.
  - `blocked` (boolean): Whether the prompt was blocked.
  - `requires_approval` (boolean): Whether the prompt requires approval.
  - `matched_policies` (array of objects): The policies that matched the prompt.
- `evaluation_time` (string): The time when the evaluation was performed.

## Policy Cache API

### Refresh Policy Cache

Refreshes the policy cache by fetching the latest policies from the Policy Service.

**Endpoint:** `POST /policies/refresh`

**Response:**

```json
{
  "success": true,
  "message": "Policy cache refreshed successfully",
  "policy_count": 10,
  "timestamp": "2023-01-01T00:00:00Z"
}
```

### Get Policy Cache Status

Gets the status of the policy cache.

**Endpoint:** `GET /policies/status`

**Response:**

```json
{
  "policy_count": 10,
  "last_refresh": "2023-01-01T00:00:00Z",
  "active_policies": 8,
  "draft_policies": 2,
  "deprecated_policies": 0,
  "archived_policies": 0
}
```

## Health Check API

### Health Check

Checks the health of the RGE Service.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "service": "ACGS-PGP Runtime Governance Engine",
  "version": "0.1.0",
  "policy_cache": {
    "status": "healthy",
    "policy_count": 10,
    "last_refresh": "2023-01-01T00:00:00Z"
  },
  "dependencies": {
    "policy_service": "healthy"
  }
}
```

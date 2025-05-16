# ACGS-PGP Synthesis Service

The Synthesis Service is a core component of the ACGS-PGP (Artificial Constitution Governance System - Policy Governance Platform). It's responsible for generating Policy Intermediate Representations (PIRs) from high-level policy intents using Large Language Models (LLMs).

## Features

- **Policy Synthesis**: Convert natural language policy intents into structured PIRs
- **LLM Integration**: Leverages OpenAI's GPT models for policy generation
- **RESTful API**: Provides endpoints for policy synthesis and management
- **Database Integration**: Stores synthesized policies in PostgreSQL
- **Kafka Integration**: Publishes policy update events to Kafka topics

## API Endpoints

### Synthesize a Policy

```http
POST /api/v1/synthesize
```

**Request Body:**
```json
{
  "policy_intent": "Prevent sharing of personally identifiable information (PII)",
  "context": {
    "domain": "customer service",
    "regulations": ["GDPR", "CCPA"]
  },
  "constraints": [
    "Must detect and handle various PII formats (SSN, credit cards, etc.)",
    "Should log PII detection events for auditing purposes"
  ]
}
```

**Response:**
```json
{
  "policy": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "PII Protection Policy",
    "description": "Prevents sharing of personally identifiable information",
    "status": "draft",
    "version": 1,
    "trigger_conditions": [
      {
        "condition_type": "prompt_pattern",
        "parameters": {
          "patterns": ["ssn", "credit card", "social security"]
        },
        "description": "Detect PII in the prompt"
      }
    ],
    "governance_actions": [
      {
        "action_type": "block_execution",
        "parameters": {
          "message": "This prompt contains PII and cannot be processed"
        },
        "priority": 100,
        "description": "Block prompts containing PII"
      }
    ],
    "tags": ["security", "compliance"],
    "metadata": {
      "generated_by": "synthesis-service",
      "source_intent": "Prevent sharing of personally identifiable information (PII)"
    },
    "created_at": "2023-06-15T12:00:00Z",
    "updated_at": "2023-06-15T12:00:00Z",
    "created_by": "system",
    "updated_by": "system"
  },
  "explanation": "This policy detects common PII patterns in prompts and blocks execution to prevent data leakage.",
  "confidence": 0.95,
  "warnings": []
}
```

### Get Synthesis Examples

```http
GET /api/v1/synthesize/examples
```

**Response:**
```json
[
  {
    "intent": "Prevent sharing of personally identifiable information (PII)",
    "context": {
      "domain": "customer service",
      "regulations": ["GDPR", "CCPA"]
    },
    "constraints": [
      "Must detect and handle various PII formats (SSN, credit cards, etc.)",
      "Should log PII detection events for auditing purposes"
    ]
  },
  {
    "intent": "Ensure all financial advice includes appropriate disclaimers",
    "context": {
      "domain": "financial services",
      "regulations": ["FINRA", "SEC"]
    },
    "constraints": [
      "Must include standard investment disclaimers",
      "Should require human review for complex financial advice"
    ]
  }
]
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `POSTGRES_SERVER` | PostgreSQL server host | `postgres` |
| `POSTGRES_PORT` | PostgreSQL server port | `5432` |
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `POSTGRES_DB` | PostgreSQL database name | `acgs_policy` |
| `SQL_ECHO` | Log SQL queries | `false` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka bootstrap servers | `kafka:29092,localhost:9093` |
| `KAFKA_POLICY_UPDATES_TOPIC` | Kafka topic for policy updates | `policy-updates` |
| `LLM_API_KEY` | OpenAI API key | - |
| `LLM_MODEL` | OpenAI model to use | `gpt-4` |
| `LLM_TEMPERATURE` | Sampling temperature for the LLM | `0.2` |
| `POLICY_SERVICE_URL` | URL of the Policy Service | `http://policy-service:8000` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://localhost:8002"]` |

## Running Locally

1. Make sure you have Docker and Docker Compose installed
2. Clone the repository
3. Copy `.env.example` to `.env` and update the environment variables
4. Run the service using Docker Compose:

```bash
docker-compose up -d synthesis-service
```

## Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Run the development server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Testing

To run the tests:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

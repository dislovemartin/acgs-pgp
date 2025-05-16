# ACGS-PGP (Artificial Constitution Governance System - Policy Governance Platform)

A comprehensive policy governance platform for managing and enforcing AI policies in real-time.

## Architecture

The system is built using a microservices architecture with the following components:

1. **Policy Service**: Manages policy definitions (P-IRs) with CRUD operations and versioning.
2. **RGE (Runtime Governance Engine)**: Evaluates prompts and actions against active policies.
3. **Kafka**: Handles real-time policy updates and event streaming.
4. **PostgreSQL**: Persistent storage for policies and metadata.
5. **PgAdmin**: Web-based administration tool for PostgreSQL (optional).
6. **Kafka UI**: Web-based UI for monitoring Kafka topics and messages (optional).

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+

### Environment Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd acgs-pgp
   ```

2. Copy the example environment files:
   ```bash
   cp services/policy_service/.env.example services/policy_service/.env
   cp services/rge_service/.env.example services/rge_service/.env
   ```

3. Update the environment variables in the `.env` files as needed.

### Running the Services

Start all services using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Policy Service at http://localhost:8000
- RGE Service at http://localhost:8001
- PostgreSQL on port 5432
- PgAdmin at http://localhost:5050 (email: admin@acgs.local, password: admin)
- Kafka UI at http://localhost:8080

### Verifying the Services

1. **Policy Service Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **RGE Service Health Check**:
   ```bash
   curl http://localhost:8001/health
   ```

## API Documentation

Once the services are running, you can access the interactive API documentation:

- **Policy Service API Docs**: http://localhost:8000/docs
- **RGE Service API Docs**: http://localhost:8001/docs

## Development

### Project Structure

```
acgs-pgp/
├── common/                    # Shared code and schemas
│   └── schemas/               # Pydantic schemas shared across services
│       └── pir.py             # Policy Intermediate Representation schemas
├── services/
│   ├── policy_service/       # Policy management service
│   │   ├── app/
│   │   │   ├── api/         # API routes
│   │   │   ├── core/         # Core application code
│   │   │   ├── crud/         # Database operations
│   │   │   ├── db/           # Database configuration
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   └── main.py       # FastAPI application
│   │   ├── Dockerfile        # Container configuration
│   │   └── requirements.txt  # Python dependencies
│   │
│   └── rge_service/         # Runtime Governance Engine
│       ├── app/
│       │   ├── api/         # API routes
│       │   ├── core/         # Core application code
│       │   ├── engine/       # Policy evaluation engine
│       │   └── main.py       # FastAPI application
│       ├── Dockerfile        # Container configuration
│       └── requirements.txt  # Python dependencies
│
├── docker-compose.yml       # Service orchestration
└── README.md                 # This file
```

### Adding a New Service

1. Create a new directory under `services/` for your service.
2. Set up the basic structure with `app/`, `Dockerfile`, and `requirements.txt`.
3. Add the service configuration to `docker-compose.yml`.
4. Update the documentation as needed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

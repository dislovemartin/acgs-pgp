# ACGS-PGP API Documentation

This directory contains API documentation for the ACGS-PGP system.

## Document Metadata

- **Version:** 1.0.0
- **Last Updated:** [YYYY-MM-DD]
- **Author:** [Author Name]
- **Status:** Approved

## API Documentation

The ACGS-PGP system consists of several microservices, each with its own API. This directory contains documentation for each service API.

### Service APIs

1. [Policy Service API](policy_service.md) - API for managing policies (P-IRs) and AI Constitutions
2. [RGE Service API](rge_service.md) - API for evaluating policies against prompts
3. [Synthesis Service API](synthesis_service.md) - API for synthesizing policies from natural language intents

### API Standards

All ACGS-PGP APIs follow these standards:

1. **RESTful Design** - APIs follow REST principles
2. **JSON Format** - Request and response bodies use JSON format
3. **OpenAPI Specification** - APIs are documented using OpenAPI Specification
4. **Versioning** - APIs are versioned using URL path versioning (e.g., `/api/v1/`)
5. **Authentication** - APIs use token-based authentication
6. **Error Handling** - APIs use standard error response format

### API Documentation Format

Each API documentation file includes:

1. **Base URL** - The base URL for the API
2. **Authentication** - How to authenticate with the API
3. **Endpoints** - Detailed documentation for each endpoint
4. **Request/Response Examples** - Examples of API requests and responses
5. **Error Codes** - List of possible error codes and their meanings
6. **Rate Limiting** - Information about API rate limiting

## Contributing

To contribute to the API documentation:

1. Use the [API Documentation Template](../document_management/templates/api_documentation_template.md)
2. Follow the [Documentation Guidelines](../document_management/guidelines/document_creation.md)
3. Validate your documentation using the validation script

# [Service Name] API Documentation

This document describes the API endpoints for the [Service Name] in the ACGS-PGP system.

## Document Metadata

- **Version:** [e.g., 1.0.0]
- **Last Updated:** [YYYY-MM-DD]
- **Author:** [Author Name]
- **Status:** [Draft/Review/Approved]

## Base URL

```
http://[hostname]:[port]/api/[version]
```

## Authentication

[Describe authentication methods, if any]

## Endpoints

### [Endpoint Group Name]

#### [Operation Name]

[Brief description of what this endpoint does]

**Endpoint:** `[HTTP Method] [Path]`

**Path Parameters:**

- `[parameter_name]` ([type], [required/optional]): [Description]

**Query Parameters:**

- `[parameter_name]` ([type], [required/optional]): [Description]

**Request Body:**

```json
{
  "[field_name]": "[field_value]",
  "[field_name]": {
    "[nested_field]": "[value]"
  }
}
```

**Request Fields:**

- `[field_name]` ([type], [required/optional]): [Description]

**Response:**

```json
{
  "[field_name]": "[field_value]",
  "[field_name]": {
    "[nested_field]": "[value]"
  }
}
```

**Response Fields:**

- `[field_name]` ([type]): [Description]

**Status Codes:**

- `200 OK`: [Description]
- `400 Bad Request`: [Description]
- `401 Unauthorized`: [Description]
- `403 Forbidden`: [Description]
- `404 Not Found`: [Description]
- `500 Internal Server Error`: [Description]

**Example:**

Request:
```http
[HTTP Method] [Path]
Content-Type: application/json

{
  "[field_name]": "[field_value]"
}
```

Response:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "[field_name]": "[field_value]"
}
```

## Error Handling

[Describe common error formats and handling]

## Rate Limiting

[Describe rate limiting policies, if any]

## Versioning

[Describe API versioning strategy]

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| [version] | [date] | [changes] |

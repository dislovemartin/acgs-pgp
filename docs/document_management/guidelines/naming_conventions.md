# ACGS-PGP Documentation Naming Conventions

This document defines the naming conventions for documentation in the ACGS-PGP project.

## Document Metadata

- **Version:** 1.0.0
- **Last Updated:** [YYYY-MM-DD]
- **Author:** [Author Name]
- **Status:** Approved

## File Naming Conventions

### General Rules

1. Use lowercase letters for all filenames
2. Use hyphens (-) to separate words in filenames
3. Use descriptive names that indicate the content of the document
4. Include version numbers in filenames only when multiple versions need to be maintained simultaneously
5. Use standard file extensions (.md for Markdown, .json for JSON, etc.)

### Specific Document Types

#### API Documentation

Format: `api-[service-name].md`

Examples:
- `api-policy-service.md`
- `api-rge-service.md`
- `api-synthesis-service.md`

#### Architecture Documentation

Format: `architecture-[component-name].md`

Examples:
- `architecture-overview.md`
- `architecture-policy-service.md`
- `architecture-rge-service.md`

#### Development Guides

Format: `dev-guide-[topic].md`

Examples:
- `dev-guide-setup.md`
- `dev-guide-contribution.md`
- `dev-guide-testing.md`

#### Operational Guides

Format: `ops-guide-[topic].md`

Examples:
- `ops-guide-deployment.md`
- `ops-guide-monitoring.md`
- `ops-guide-backup.md`

#### User Documentation

Format: `user-guide-[topic].md`

Examples:
- `user-guide-getting-started.md`
- `user-guide-policy-creation.md`
- `user-guide-troubleshooting.md`

#### Policy Documents

Format: `policy-[type]-[name].md`

Examples:
- `policy-pir-pii-protection.md`
- `policy-constitution-privacy.md`

#### Technical Specifications

Format: `spec-[component]-[feature].md`

Examples:
- `spec-rge-evaluation-engine.md`
- `spec-synthesis-llm-integration.md`

#### Test Documentation

Format: `test-[type]-[component].md`

Examples:
- `test-plan-policy-service.md`
- `test-cases-rge-service.md`
- `test-report-synthesis-service.md`

## Directory Structure

### Top-Level Directories

- `docs/`: All documentation
  - `api/`: API documentation
  - `architecture/`: Architecture documentation
  - `development/`: Development guides
  - `operations/`: Operational guides
  - `user/`: User documentation
  - `policy/`: Policy documents
  - `specifications/`: Technical specifications
  - `testing/`: Test documentation
  - `document_management/`: Document management system

### Subdirectory Structure

Each top-level directory may have subdirectories for specific components or topics.

Example:
```
docs/
├── api/
│   ├── policy-service/
│   ├── rge-service/
│   └── synthesis-service/
├── architecture/
│   ├── overview/
│   ├── components/
│   └── data-flow/
```

## Version Control

### Version Numbers

Use semantic versioning (MAJOR.MINOR.PATCH) for document versions.

- MAJOR: Significant changes that may require updates to related documents
- MINOR: Additions or changes that don't break existing content
- PATCH: Minor corrections or clarifications

### Version History

Maintain a version history section at the end of each document with the following format:

```
## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0   | YYYY-MM-DD | Author Name | Initial version |
| 1.0.1   | YYYY-MM-DD | Author Name | Fixed typos |
| 1.1.0   | YYYY-MM-DD | Author Name | Added section on X |
```

## Document Status

Use the following status values for documents:

- **Draft**: Initial creation or major revision, not yet ready for review
- **Review**: Ready for review by peers
- **Approved**: Reviewed and approved for use
- **Deprecated**: No longer current, but kept for reference
- **Archived**: No longer relevant, kept for historical purposes

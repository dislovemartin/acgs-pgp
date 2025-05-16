# ACGS-PGP Document Management System Usage Guide

This document provides a guide for using the ACGS-PGP Document Management System.

## Document Metadata

- **Version:** 1.0.0
- **Last Updated:** [YYYY-MM-DD]
- **Author:** [Author Name]
- **Status:** Approved

## Overview

The ACGS-PGP Document Management System (DMS) provides a comprehensive approach to document analysis, categorization, organization, and management. This guide explains how to use the DMS for various documentation tasks.

## Getting Started

### Accessing the Documentation

The ACGS-PGP documentation is stored in the `docs/` directory of the repository. The documentation is organized into categories:

1. **API Documentation** (`docs/api/`) - API endpoints, request/response formats, examples
2. **Architecture Documentation** (`docs/architecture/`) - System design, component interactions, data flows
3. **Development Documentation** (`docs/development/`) - Setup instructions, coding standards, contribution guidelines
4. **Operations Documentation** (`docs/operations/`) - Deployment, monitoring, maintenance procedures
5. **User Documentation** (`docs/user/`) - End-user guides, tutorials, FAQs
6. **Policy Documentation** (`docs/policy/`) - P-IR definitions, AI Constitution principles
7. **Technical Specifications** (`docs/specifications/`) - Detailed technical requirements and implementations
8. **Test Documentation** (`docs/testing/`) - Test plans, test cases, test reports

The Document Management System itself is located in the `docs/document_management/` directory.

### Finding Documents

To find documents in the repository, you can:

1. **Browse the Directory Structure** - Navigate through the directory structure to find documents
2. **Search the Document Catalog** - Browse the catalog files in `docs/document_management/catalog/`
3. **Use the Search Script** - Run the search script to find documents by keyword, tag, or type

#### Using the Search Script

The search script provides a simple way to find documents in the repository:

```bash
python docs/document_management/scripts/search_documents.py --content "your search query"
```

To search for documents with a specific tag:

```bash
python docs/document_management/scripts/search_documents.py --tag "tag-name"
```

To search for documents of a specific type:

```bash
python docs/document_management/scripts/search_documents.py --type "document-type"
```

## Creating Documents

### Using Templates

When creating a new document, start with the appropriate template from the `docs/document_management/templates/` directory:

1. **API Documentation Template** (`api_documentation_template.md`)
2. **Architecture Documentation Template** (`architecture_documentation_template.md`)
3. **Development Guide Template** (`development_guide_template.md`)
4. **Operational Guide Template** (`operational_guide_template.md`)
5. **User Documentation Template** (`user_documentation_template.md`)
6. **Policy Document Template** (`policy_document_template.md`)
7. **Technical Specification Template** (`technical_specification_template.md`)
8. **Test Documentation Template** (`test_documentation_template.md`)
9. **Service Documentation Template** (`service_documentation_template.md`)

To use a template:

1. Copy the template file to the appropriate location in the codebase
2. Rename the file according to the naming convention
3. Fill in the template with the appropriate content
4. Update the document catalog with the new document metadata

### Following Guidelines

When creating or modifying documents, follow the guidelines in the `docs/document_management/guidelines/` directory:

1. **Naming Conventions** (`naming_conventions.md`) - Guidelines for naming documents
2. **Document Creation** (`document_creation.md`) - Guidelines for creating and modifying documents
3. **Document Validation** (`document_validation.md`) - Guidelines for validating documents

### Validating Documents

Before submitting a document, validate it against the quality guidelines:

```bash
python docs/document_management/scripts/validate_documents.py path/to/your/document.md
```

This will check the document for common issues and provide feedback on how to improve it.

## Maintaining Documents

### Updating Documents

When updating a document:

1. Update the document's metadata (version, last updated, author)
2. Make the necessary changes to the content
3. Update the version history section with a summary of changes
4. Validate the document using the validation script
5. Update the document catalog if necessary

### Archiving Documents

When a document becomes obsolete:

1. Update the document's status to "Deprecated" or "Archived"
2. Update the document catalog to reflect the new status
3. Move the document to an archive directory if appropriate
4. Create a new document to replace it if needed

## Document Management Scripts

The DMS includes several scripts to help manage documentation:

### Document Analysis Script

The document analysis script analyzes all Markdown documents in the repository and generates catalog files:

```bash
python docs/document_management/scripts/analyze_documents.py
```

### Document Validation Script

The document validation script checks documents against quality guidelines:

```bash
python docs/document_management/scripts/validate_documents.py [path]
```

### Document Search Script

The document search script provides a simple search interface:

```bash
python docs/document_management/scripts/search_documents.py --content "your search query"
```

### Directory Structure Generator

The directory structure generator creates the documentation directory structure:

```bash
python docs/document_management/scripts/generate_structure.py [--placeholders]
```

## Best Practices

1. **Use Templates** - Always start with the appropriate template
2. **Follow Guidelines** - Adhere to the naming conventions and creation guidelines
3. **Validate Documents** - Run the validation script before submitting documents
4. **Update Metadata** - Keep document metadata up to date
5. **Maintain the Catalog** - Update the catalog when adding or modifying documents
6. **Use Version Control** - Track document changes using version control
7. **Review Regularly** - Regularly review documents for accuracy and completeness

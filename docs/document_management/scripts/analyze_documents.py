#!/usr/bin/env python3
"""
Document Analysis and Cataloging Script

This script analyzes all Markdown documents in the repository and generates
catalog files based on document type, purpose, and content.
"""

import os
import re
import json
import yaml
import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
CATALOG_DIR = REPO_ROOT / "docs" / "document_management" / "catalog"
EXCLUDE_DIRS = [".git", "node_modules", "venv", "__pycache__"]
DOCUMENT_TYPES = {
    "api": ["api", "endpoint", "request", "response", "http"],
    "architecture": ["architecture", "design", "component", "system", "diagram"],
    "development": ["development", "setup", "install", "contribute", "coding"],
    "operations": ["operations", "deploy", "monitor", "maintain", "backup"],
    "user": ["user", "guide", "tutorial", "how-to", "faq"],
    "policy": ["policy", "pir", "constitution", "governance", "compliance"],
    "specifications": ["specification", "spec", "requirement", "technical"],
    "testing": ["test", "qa", "quality", "validation", "verification"]
}

def find_markdown_files():
    """Find all Markdown files in the repository."""
    markdown_files = []
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                markdown_files.append(file_path)
    
    return markdown_files

def extract_metadata(file_path):
    """Extract metadata from a Markdown file."""
    metadata = {
        "title": None,
        "path": str(file_path.relative_to(REPO_ROOT)),
        "type": None,
        "purpose": None,
        "content_summary": None,
        "last_updated": None,
        "author": None,
        "tags": []
    }
    
    # Read the file content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return metadata
    
    # Extract title (first h1)
    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1)
    
    # Extract metadata block if present
    metadata_match = re.search(r"## Document Metadata\s+(.+?)(?=^##|\Z)", content, re.MULTILINE | re.DOTALL)
    if metadata_match:
        metadata_block = metadata_match.group(1)
        
        # Extract version
        version_match = re.search(r"\*\*Version:\*\* (.+)", metadata_block)
        if version_match:
            metadata["version"] = version_match.group(1)
        
        # Extract last updated
        updated_match = re.search(r"\*\*Last Updated:\*\* (.+)", metadata_block)
        if updated_match:
            metadata["last_updated"] = updated_match.group(1)
        
        # Extract author
        author_match = re.search(r"\*\*Author:\*\* (.+)", metadata_block)
        if author_match:
            metadata["author"] = author_match.group(1)
        
        # Extract status
        status_match = re.search(r"\*\*Status:\*\* (.+)", metadata_block)
        if status_match:
            metadata["status"] = status_match.group(1)
    
    # Extract content summary (first paragraph after title)
    summary_match = re.search(r"^# .+\s+(.+?)(?=^#|\Z)", content, re.MULTILINE | re.DOTALL)
    if summary_match:
        summary = summary_match.group(1).strip()
        # Limit to first paragraph
        first_para = summary.split("\n\n")[0]
        metadata["content_summary"] = first_para
    
    # Determine document type based on content
    doc_type = None
    max_score = 0
    
    for type_name, keywords in DOCUMENT_TYPES.items():
        score = sum(1 for keyword in keywords if keyword.lower() in content.lower())
        if score > max_score:
            max_score = score
            doc_type = type_name
    
    metadata["type"] = doc_type
    
    # Extract tags from content
    tags = set()
    for type_name, keywords in DOCUMENT_TYPES.items():
        for keyword in keywords:
            if keyword.lower() in content.lower():
                tags.add(keyword)
    
    # Add filename-based tags
    filename = file_path.stem
    for word in re.findall(r"[a-zA-Z]+", filename):
        if len(word) > 3:  # Skip short words
            tags.add(word.lower())
    
    metadata["tags"] = list(tags)
    
    # Determine purpose based on content and type
    if doc_type == "api":
        metadata["purpose"] = "Describes API endpoints, request/response formats, and examples"
    elif doc_type == "architecture":
        metadata["purpose"] = "Describes system architecture, components, and interactions"
    elif doc_type == "development":
        metadata["purpose"] = "Provides guidance for developers working on the project"
    elif doc_type == "operations":
        metadata["purpose"] = "Provides guidance for operating and maintaining the system"
    elif doc_type == "user":
        metadata["purpose"] = "Provides guidance for end users of the system"
    elif doc_type == "policy":
        metadata["purpose"] = "Defines policies and governance rules for the system"
    elif doc_type == "specifications":
        metadata["purpose"] = "Specifies technical requirements and implementations"
    elif doc_type == "testing":
        metadata["purpose"] = "Describes testing procedures and results"
    
    return metadata

def generate_catalog_files(documents):
    """Generate catalog files based on document type."""
    # Group documents by type
    documents_by_type = defaultdict(list)
    for doc in documents:
        doc_type = doc["type"] or "uncategorized"
        documents_by_type[doc_type].append(doc)
    
    # Create catalog directory if it doesn't exist
    os.makedirs(CATALOG_DIR, exist_ok=True)
    
    # Generate catalog files
    for doc_type, docs in documents_by_type.items():
        catalog_file = CATALOG_DIR / f"{doc_type}.md"
        
        with open(catalog_file, "w", encoding="utf-8") as f:
            f.write(f"# {doc_type.title()} Documentation Catalog\n\n")
            f.write(f"This catalog contains metadata about all {doc_type} documentation in the ACGS-PGP codebase.\n\n")
            
            for doc in sorted(docs, key=lambda x: x["title"] or ""):
                if doc["title"]:
                    f.write(f"## {doc['title']}\n\n")
                else:
                    f.write(f"## {Path(doc['path']).name}\n\n")
                
                f.write("| Metadata | Value |\n")
                f.write("|----------|-------|\n")
                f.write(f"| **Title** | {doc['title'] or 'Untitled'} |\n")
                f.write(f"| **Path** | `{doc['path']}` |\n")
                f.write(f"| **Type** | {doc['type'] or 'Unknown'} |\n")
                f.write(f"| **Purpose** | {doc['purpose'] or 'Unknown'} |\n")
                f.write(f"| **Content Summary** | {doc['content_summary'] or 'No summary available'} |\n")
                f.write(f"| **Last Updated** | {doc['last_updated'] or 'Unknown'} |\n")
                f.write(f"| **Author** | {doc['author'] or 'Unknown'} |\n")
                f.write(f"| **Tags** | {', '.join(doc['tags'])} |\n")
                f.write("\n")
    
    # Generate index file
    with open(CATALOG_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write("# ACGS-PGP Document Catalog\n\n")
        f.write("This directory contains the document catalog for the ACGS-PGP project. ")
        f.write("The catalog provides a searchable index of all documents in the codebase, ")
        f.write("categorized by type, purpose, and content.\n\n")
        
        f.write("## Catalog Structure\n\n")
        f.write("The catalog is organized into the following categories:\n\n")
        
        for doc_type in sorted(documents_by_type.keys()):
            count = len(documents_by_type[doc_type])
            f.write(f"1. **{doc_type.title()} Documents** (`{doc_type}.md`): {count} documents\n")
        
        f.write("\n## Document Statistics\n\n")
        f.write(f"Total documents: {sum(len(docs) for docs in documents_by_type.values())}\n\n")
        
        f.write("| Document Type | Count |\n")
        f.write("|--------------|-------|\n")
        for doc_type in sorted(documents_by_type.keys()):
            count = len(documents_by_type[doc_type])
            f.write(f"| {doc_type.title()} | {count} |\n")

def main():
    """Main function."""
    print("ACGS-PGP Document Analysis and Cataloging Script")
    print("===============================================")
    
    print("\nFinding Markdown files...")
    markdown_files = find_markdown_files()
    print(f"Found {len(markdown_files)} Markdown files.")
    
    print("\nExtracting metadata...")
    documents = []
    for file_path in markdown_files:
        print(f"Processing {file_path.relative_to(REPO_ROOT)}...")
        metadata = extract_metadata(file_path)
        documents.append(metadata)
    
    print("\nGenerating catalog files...")
    generate_catalog_files(documents)
    
    print("\nDone!")

if __name__ == "__main__":
    main()

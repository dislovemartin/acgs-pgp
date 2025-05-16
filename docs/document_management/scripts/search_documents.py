#!/usr/bin/env python3
"""
Document Search Script

This script provides a simple search interface for finding documents in the repository.
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
CATALOG_DIR = REPO_ROOT / "docs" / "document_management" / "catalog"
EXCLUDE_DIRS = [".git", "node_modules", "venv", "__pycache__"]

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

def search_documents(query, search_content=False):
    """Search for documents matching the query."""
    markdown_files = find_markdown_files()
    results = []
    
    for file_path in markdown_files:
        rel_path = file_path.relative_to(REPO_ROOT)
        
        # Always search in filename and path
        if query.lower() in str(rel_path).lower():
            results.append({
                "path": str(rel_path),
                "match_type": "path",
                "match_context": str(rel_path)
            })
            continue
        
        # Read the file content if needed
        if search_content:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Search in title
                title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
                if title_match and query.lower() in title_match.group(1).lower():
                    results.append({
                        "path": str(rel_path),
                        "match_type": "title",
                        "match_context": title_match.group(1)
                    })
                    continue
                
                # Search in content
                if query.lower() in content.lower():
                    # Find the context of the match
                    index = content.lower().find(query.lower())
                    start = max(0, index - 50)
                    end = min(len(content), index + len(query) + 50)
                    context = content[start:end]
                    
                    # Clean up context
                    context = re.sub(r"\s+", " ", context).strip()
                    if start > 0:
                        context = "..." + context
                    if end < len(content):
                        context = context + "..."
                    
                    results.append({
                        "path": str(rel_path),
                        "match_type": "content",
                        "match_context": context
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return results

def search_by_tag(tag):
    """Search for documents with a specific tag."""
    results = []
    
    # Check if catalog files exist
    if not CATALOG_DIR.exists():
        print("Catalog directory not found. Run analyze_documents.py first.")
        return results
    
    # Search in all catalog files
    for catalog_file in CATALOG_DIR.glob("*.md"):
        if catalog_file.name == "README.md":
            continue
        
        try:
            with open(catalog_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find document sections
            sections = re.split(r"^## ", content, flags=re.MULTILINE)[1:]
            
            for section in sections:
                # Check if the tag is in the tags list
                tags_match = re.search(r"\| \*\*Tags\*\* \| (.+) \|", section)
                if tags_match and tag.lower() in tags_match.group(1).lower():
                    # Extract document path
                    path_match = re.search(r"\| \*\*Path\*\* \| `(.+)` \|", section)
                    if path_match:
                        path = path_match.group(1)
                        
                        # Extract document title
                        title_match = re.search(r"^(.+?)\n", section)
                        title = title_match.group(1) if title_match else "Untitled"
                        
                        results.append({
                            "path": path,
                            "match_type": "tag",
                            "match_context": f"Tag: {tag} in document: {title}"
                        })
        except Exception as e:
            print(f"Error reading {catalog_file}: {e}")
    
    return results

def search_by_type(doc_type):
    """Search for documents of a specific type."""
    results = []
    
    # Check if catalog files exist
    if not CATALOG_DIR.exists():
        print("Catalog directory not found. Run analyze_documents.py first.")
        return results
    
    # Check if the type-specific catalog file exists
    catalog_file = CATALOG_DIR / f"{doc_type}.md"
    if not catalog_file.exists():
        print(f"No catalog file found for type: {doc_type}")
        return results
    
    try:
        with open(catalog_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find document sections
        sections = re.split(r"^## ", content, flags=re.MULTILINE)[1:]
        
        for section in sections:
            # Extract document path
            path_match = re.search(r"\| \*\*Path\*\* \| `(.+)` \|", section)
            if path_match:
                path = path_match.group(1)
                
                # Extract document title
                title_match = re.search(r"^(.+?)\n", section)
                title = title_match.group(1) if title_match else "Untitled"
                
                results.append({
                    "path": path,
                    "match_type": "type",
                    "match_context": f"Type: {doc_type} - {title}"
                })
    except Exception as e:
        print(f"Error reading {catalog_file}: {e}")
    
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Search for documents in the repository")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--content", action="store_true", help="Search in document content")
    parser.add_argument("--tag", help="Search for documents with a specific tag")
    parser.add_argument("--type", dest="doc_type", help="Search for documents of a specific type")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()
    
    if not args.query and not args.tag and not args.doc_type:
        parser.print_help()
        return
    
    results = []
    
    if args.query:
        print(f"Searching for '{args.query}'...")
        results.extend(search_documents(args.query, args.content))
    
    if args.tag:
        print(f"Searching for documents with tag '{args.tag}'...")
        results.extend(search_by_tag(args.tag))
    
    if args.doc_type:
        print(f"Searching for documents of type '{args.doc_type}'...")
        results.extend(search_by_type(args.doc_type))
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nFound {len(results)} matching documents:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['path']}")
            print(f"   Match: {result['match_type']}")
            print(f"   Context: {result['match_context']}")
            print()

if __name__ == "__main__":
    main()

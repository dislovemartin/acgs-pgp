#!/usr/bin/env python3
"""
Document Validation Script

This script validates Markdown documents against quality guidelines and reports issues.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
TEMPLATES_DIR = REPO_ROOT / "docs" / "document_management" / "templates"
EXCLUDE_DIRS = [".git", "node_modules", "venv", "__pycache__"]

# Validation rules
RULES = {
    "has_title": {
        "description": "Document has a title (H1)",
        "pattern": r"^# .+$",
        "severity": "error"
    },
    "has_metadata": {
        "description": "Document has metadata section",
        "pattern": r"## Document Metadata",
        "severity": "warning"
    },
    "has_version": {
        "description": "Document has version information",
        "pattern": r"\*\*Version:\*\* .+",
        "severity": "warning"
    },
    "has_date": {
        "description": "Document has last updated date",
        "pattern": r"\*\*Last Updated:\*\* .+",
        "severity": "warning"
    },
    "has_author": {
        "description": "Document has author information",
        "pattern": r"\*\*Author:\*\* .+",
        "severity": "warning"
    },
    "has_status": {
        "description": "Document has status information",
        "pattern": r"\*\*Status:\*\* .+",
        "severity": "warning"
    },
    "no_broken_links": {
        "description": "Document has no broken internal links",
        "pattern": r"\[.+?\]\((?!http)[^)]+\)",
        "severity": "error",
        "custom_check": "check_internal_links"
    },
    "no_todo": {
        "description": "Document has no TODO markers",
        "pattern": r"TODO|FIXME",
        "severity": "warning"
    },
    "no_empty_sections": {
        "description": "Document has no empty sections",
        "pattern": r"^#+\s+.+\s+^#+",
        "severity": "warning",
        "custom_check": "check_empty_sections"
    },
    "proper_heading_hierarchy": {
        "description": "Document has proper heading hierarchy",
        "pattern": None,
        "severity": "warning",
        "custom_check": "check_heading_hierarchy"
    },
    "code_blocks_have_language": {
        "description": "Code blocks have language specified",
        "pattern": r"```\s*$",
        "severity": "warning"
    }
}

def find_markdown_files(path=None):
    """Find all Markdown files in the repository or specific path."""
    if path:
        if os.path.isfile(path) and path.endswith(".md"):
            return [Path(path)]
        elif os.path.isdir(path):
            root_dir = Path(path)
        else:
            print(f"Error: {path} is not a valid Markdown file or directory")
            return []
    else:
        root_dir = REPO_ROOT
    
    markdown_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                markdown_files.append(file_path)
    
    return markdown_files

def check_internal_links(content, file_path):
    """Check for broken internal links."""
    issues = []
    link_pattern = r"\[.+?\]\((?!http)([^)]+)\)"
    
    for match in re.finditer(link_pattern, content, re.MULTILINE):
        link = match.group(1)
        
        # Skip anchor links
        if link.startswith("#"):
            continue
        
        # Resolve relative path
        if not link.startswith("/"):
            link_path = file_path.parent / link
        else:
            link_path = REPO_ROOT / link.lstrip("/")
        
        # Check if file exists
        if not link_path.exists():
            issues.append(f"Broken internal link: {link}")
    
    return issues

def check_empty_sections(content, file_path):
    """Check for empty sections."""
    issues = []
    lines = content.split("\n")
    
    for i in range(len(lines) - 1):
        if re.match(r"^#+\s+.+$", lines[i]) and i + 1 < len(lines) and re.match(r"^#+\s+.+$", lines[i + 1]):
            issues.append(f"Empty section: {lines[i]}")
    
    return issues

def check_heading_hierarchy(content, file_path):
    """Check for proper heading hierarchy."""
    issues = []
    lines = content.split("\n")
    current_level = 0
    
    for line in lines:
        if line.startswith("#"):
            level = len(re.match(r"^(#+)", line).group(1))
            
            if current_level == 0:
                # First heading should be H1
                if level != 1:
                    issues.append(f"First heading should be H1, found H{level}: {line}")
            elif level > current_level + 1:
                # Heading level should not skip levels
                issues.append(f"Heading level skipped from H{current_level} to H{level}: {line}")
            
            current_level = level
    
    return issues

def validate_document(file_path):
    """Validate a Markdown document against quality guidelines."""
    issues = defaultdict(list)
    
    # Read the file content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        issues["error"].append(f"Error reading file: {e}")
        return issues
    
    # Check each rule
    for rule_id, rule in RULES.items():
        severity = rule["severity"]
        
        if rule.get("custom_check"):
            # Run custom check function
            check_func = globals()[rule["custom_check"]]
            custom_issues = check_func(content, file_path)
            if custom_issues:
                for issue in custom_issues:
                    issues[severity].append(f"{rule['description']}: {issue}")
        elif rule["pattern"]:
            # Check pattern
            if rule_id.startswith("no_"):
                # Rule checks for absence of pattern
                if re.search(rule["pattern"], content, re.MULTILINE):
                    issues[severity].append(rule["description"])
            else:
                # Rule checks for presence of pattern
                if not re.search(rule["pattern"], content, re.MULTILINE):
                    issues[severity].append(rule["description"])
    
    return issues

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate Markdown documents against quality guidelines")
    parser.add_argument("path", nargs="?", help="Path to a specific Markdown file or directory")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues automatically")
    args = parser.parse_args()
    
    print("ACGS-PGP Document Validation Script")
    print("===================================")
    
    print("\nFinding Markdown files...")
    markdown_files = find_markdown_files(args.path)
    print(f"Found {len(markdown_files)} Markdown files.")
    
    print("\nValidating documents...")
    all_issues = {}
    error_count = 0
    warning_count = 0
    
    for file_path in markdown_files:
        rel_path = file_path.relative_to(REPO_ROOT)
        print(f"Validating {rel_path}...")
        
        issues = validate_document(file_path)
        if issues:
            all_issues[str(rel_path)] = issues
            error_count += len(issues.get("error", []))
            warning_count += len(issues.get("warning", []))
    
    print("\nValidation Results:")
    print(f"Total files: {len(markdown_files)}")
    print(f"Files with issues: {len(all_issues)}")
    print(f"Total errors: {error_count}")
    print(f"Total warnings: {warning_count}")
    
    if all_issues:
        print("\nIssues by file:")
        for file_path, issues in all_issues.items():
            print(f"\n{file_path}:")
            
            if "error" in issues:
                print("  Errors:")
                for issue in issues["error"]:
                    print(f"    - {issue}")
            
            if "warning" in issues:
                print("  Warnings:")
                for issue in issues["warning"]:
                    print(f"    - {issue}")
    
    if error_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()

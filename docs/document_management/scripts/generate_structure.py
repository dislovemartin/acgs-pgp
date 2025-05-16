#!/usr/bin/env python3
"""
Document Directory Structure Generator

This script generates the directory structure for the ACGS-PGP documentation.
"""

import os
import argparse
from pathlib import Path

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"

# Directory structure
DIRECTORY_STRUCTURE = {
    "docs": {
        "api": {
            "policy_service": {},
            "rge_service": {},
            "synthesis_service": {}
        },
        "architecture": {
            "components": {
                "policy_service": {},
                "rge_service": {},
                "synthesis_service": {},
                "kafka": {},
                "postgresql": {}
            },
            "diagrams": {
                "system_context": {},
                "container": {},
                "component": {},
                "sequence": {},
                "data_flow": {}
            },
            "decisions": {}
        },
        "development": {
            "guides": {
                "policy_service": {},
                "rge_service": {},
                "synthesis_service": {},
                "database": {},
                "api": {}
            },
            "standards": {
                "python": {},
                "javascript": {},
                "sql": {},
                "documentation": {}
            },
            "testing": {
                "unit": {},
                "integration": {},
                "e2e": {},
                "performance": {}
            },
            "debugging": {
                "guide": {},
                "common_issues": {},
                "logging": {},
                "monitoring": {}
            }
        },
        "operations": {
            "deployment": {
                "docker": {},
                "kubernetes": {},
                "cloud": {},
                "on-premises": {}
            },
            "configuration": {
                "environment": {},
                "files": {},
                "secrets": {},
                "feature-flags": {}
            },
            "monitoring": {
                "health-checks": {},
                "metrics": {},
                "logging": {},
                "alerting": {}
            },
            "maintenance": {
                "backup-restore": {},
                "database": {},
                "upgrades": {},
                "scaling": {}
            },
            "troubleshooting": {
                "common-issues": {},
                "diagnostics": {},
                "support": {}
            },
            "security": {
                "authentication": {},
                "authorization": {},
                "encryption": {},
                "compliance": {}
            }
        },
        "user": {
            "getting-started": {
                "introduction": {},
                "requirements": {},
                "installation": {},
                "first-steps": {}
            },
            "guides": {
                "policy-management": {},
                "constitution-management": {},
                "policy-synthesis": {},
                "policy-evaluation": {},
                "reporting": {}
            },
            "tutorials": {
                "creating-policy": {},
                "creating-constitution": {},
                "synthesizing-policy": {},
                "evaluating-prompt": {},
                "integrating-external": {}
            },
            "reference": {
                "api": {},
                "policy-schema": {},
                "constitution-schema": {},
                "governance-actions": {},
                "trigger-conditions": {}
            },
            "troubleshooting": {
                "common-issues": {},
                "faq": {},
                "support": {}
            }
        },
        "policy": {
            "pir": {},
            "constitution": {},
            "examples": {}
        },
        "specifications": {
            "technical": {},
            "functional": {},
            "performance": {},
            "security": {}
        },
        "testing": {
            "plans": {},
            "cases": {},
            "reports": {}
        },
        "document_management": {
            "catalog": {},
            "templates": {},
            "guidelines": {},
            "scripts": {},
            "validation": {}
        }
    }
}

def create_directory_structure(structure, base_path=REPO_ROOT):
    """Create the directory structure."""
    for name, children in structure.items():
        path = base_path / name
        if not path.exists():
            print(f"Creating directory: {path}")
            path.mkdir(parents=True, exist_ok=True)
        
        if children:
            create_directory_structure(children, path)

def create_placeholder_files(structure, base_path=REPO_ROOT, path_prefix=""):
    """Create placeholder files for leaf directories."""
    for name, children in structure.items():
        current_path = base_path / name
        current_prefix = f"{path_prefix}/{name}" if path_prefix else name
        
        if not children:
            # This is a leaf directory, create a placeholder file
            placeholder_file = current_path / "README.md"
            if not placeholder_file.exists():
                print(f"Creating placeholder file: {placeholder_file}")
                with open(placeholder_file, "w", encoding="utf-8") as f:
                    title = current_prefix.split("/")[-1].replace("-", " ").title()
                    f.write(f"# {title}\n\n")
                    f.write(f"This is a placeholder file for the {current_prefix} documentation.\n\n")
                    f.write("## Document Metadata\n\n")
                    f.write("- **Version:** 0.1.0\n")
                    f.write("- **Last Updated:** [YYYY-MM-DD]\n")
                    f.write("- **Author:** [Author Name]\n")
                    f.write("- **Status:** Draft\n\n")
                    f.write("## Overview\n\n")
                    f.write("This document will contain information about...\n\n")
                    f.write("## Content\n\n")
                    f.write("Content will be added here...\n")
        else:
            # Recursively process children
            create_placeholder_files(children, current_path, current_prefix)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate the directory structure for ACGS-PGP documentation")
    parser.add_argument("--placeholders", action="store_true", help="Create placeholder files for leaf directories")
    args = parser.parse_args()
    
    print("ACGS-PGP Document Directory Structure Generator")
    print("===============================================")
    
    print("\nCreating directory structure...")
    create_directory_structure(DIRECTORY_STRUCTURE)
    
    if args.placeholders:
        print("\nCreating placeholder files...")
        create_placeholder_files(DIRECTORY_STRUCTURE)
    
    print("\nDone!")

if __name__ == "__main__":
    main()

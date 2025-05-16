#!/usr/bin/env python3
"""
Migration script to update existing P-IRs to the new schema format.

This script:
1. Connects to the database
2. Retrieves all existing P-IRs
3. Converts them to the new schema format
4. Updates them in the database

Usage:
    python migrate_pir_schema.py --db-url <database_url>
"""

import argparse
import logging
import sys
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Add the parent directory to the path so we can import the common schemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.schemas.pir import (
    PIR, TriggerCondition, GovernanceAction, 
    TriggerConditions, PromptPattern, ContextAttribute, 
    ToolUsageRequest, ResponsePattern,
    Scope, PolicyStatus, PolicySeverity,
    TriggerConditionType, GovernanceActionType,
    ScopeModelInclusionType, ScopeUserRoleInclusionType,
    ScopeApplicationInclusionType, ScopeDataSensitivityInclusionType
)
from services.policy_service.app.models.pir import PIRModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pir_migration.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Migrate P-IRs to the new schema format')
    parser.add_argument('--db-url', required=True, help='Database URL')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes to database)')
    return parser.parse_args()

def convert_legacy_trigger_conditions(trigger_conditions):
    """Convert legacy trigger conditions to the new structured format."""
    prompt_patterns = []
    context_attributes = []
    tool_usage_requests = []
    response_patterns = []
    
    for condition in trigger_conditions:
        if condition.get('condition_type') == 'prompt_pattern':
            patterns = condition.get('parameters', {}).get('patterns', [])
            for pattern in patterns:
                prompt_patterns.append({
                    'pattern': pattern,
                    'is_regex': '\\' in pattern,  # Simple heuristic for regex patterns
                    'case_sensitive': False,
                    'description': condition.get('description', f'Pattern: {pattern}')
                })
        elif condition.get('condition_type') == 'tool_usage':
            tool_names = condition.get('parameters', {}).get('tool_names', [])
            for tool_name in tool_names:
                tool_usage_requests.append({
                    'tool_name': tool_name,
                    'parameter_constraints': None,
                    'description': condition.get('description', f'Tool: {tool_name}')
                })
        elif condition.get('condition_type') == 'content_analysis':
            # Map content analysis to response patterns
            patterns = condition.get('parameters', {}).get('patterns', [])
            for pattern in patterns:
                response_patterns.append({
                    'pattern': pattern,
                    'is_regex': '\\' in pattern,
                    'case_sensitive': False,
                    'description': condition.get('description', f'Response pattern: {pattern}')
                })
        elif condition.get('condition_type') == 'metadata_match':
            # Map metadata match to context attributes
            metadata = condition.get('parameters', {}).get('metadata', {})
            for key, value in metadata.items():
                context_attributes.append({
                    'attribute_name': key,
                    'attribute_value': value,
                    'match_type': 'exact',
                    'description': condition.get('description', f'Metadata: {key}={value}')
                })
    
    return {
        'prompt_patterns': prompt_patterns,
        'context_attributes': context_attributes,
        'tool_usage_requests': tool_usage_requests,
        'response_patterns': response_patterns,
        'custom_conditions': [],
        'condition_logic': 'ANY'
    }

def migrate_pir(pir_dict):
    """Migrate a P-IR dictionary to the new schema format."""
    # Create a copy of the original P-IR
    new_pir = pir_dict.copy()
    
    # Add new fields with default values
    if 'constitutional_references' not in new_pir:
        new_pir['constitutional_references'] = []
    
    if 'scope' not in new_pir:
        new_pir['scope'] = {
            'llm_models_inclusion': 'all',
            'llm_models_list': [],
            'user_roles_inclusion': 'all',
            'user_roles_list': [],
            'applications_inclusion': 'all',
            'applications_list': [],
            'data_sensitivity_inclusion': 'all',
            'data_sensitivity_levels': [],
            'custom_scope_attributes': {}
        }
    
    # Convert trigger conditions if they're in the legacy format (list)
    if 'trigger_conditions' in new_pir and isinstance(new_pir['trigger_conditions'], list):
        new_pir['trigger_conditions'] = convert_legacy_trigger_conditions(new_pir['trigger_conditions'])
    
    # Add severity and priority if not present
    if 'severity' not in new_pir:
        # Try to infer severity from metadata or set a default
        metadata = new_pir.get('metadata', {})
        severity_str = metadata.get('severity', 'medium')
        # Map string to enum value
        severity_map = {
            'low': 'low',
            'medium': 'medium',
            'high': 'high',
            'critical': 'critical'
        }
        new_pir['severity'] = severity_map.get(severity_str.lower(), 'medium')
    
    if 'priority' not in new_pir:
        # Try to infer priority from metadata or set a default
        metadata = new_pir.get('metadata', {})
        new_pir['priority'] = metadata.get('priority', 50)
    
    # Enhance metadata
    if 'metadata' in new_pir:
        metadata = new_pir['metadata']
        if not isinstance(metadata, dict):
            metadata = {}
        
        # Add structured metadata
        if 'author' not in metadata:
            metadata['author'] = new_pir.get('created_by', 'system')
        
        if 'created_timestamp' not in metadata:
            metadata['created_timestamp'] = new_pir.get('created_at')
        
        if 'last_updated_timestamp' not in metadata:
            metadata['last_updated_timestamp'] = new_pir.get('updated_at')
        
        if 'compliance_standards' not in metadata:
            metadata['compliance_standards'] = []
        
        if 'custom_metadata' not in metadata:
            metadata['custom_metadata'] = {}
        
        new_pir['metadata'] = metadata
    
    return new_pir

def main():
    """Main function."""
    args = parse_args()
    
    # Connect to the database
    engine = create_engine(args.db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all P-IRs
        pirs = session.query(PIRModel).all()
        logger.info(f"Found {len(pirs)} P-IRs to migrate")
        
        # Migrate each P-IR
        for pir in pirs:
            logger.info(f"Migrating P-IR {pir.id} ({pir.name})")
            
            # Convert to dictionary
            pir_dict = pir.to_dict()
            
            # Migrate to new schema
            new_pir_dict = migrate_pir(pir_dict)
            
            if not args.dry_run:
                # Update the database
                pir.constitutional_references = new_pir_dict.get('constitutional_references', [])
                pir.scope = new_pir_dict.get('scope', {})
                pir.trigger_conditions = new_pir_dict.get('trigger_conditions', {})
                pir.severity = new_pir_dict.get('severity', 'medium')
                pir.priority = new_pir_dict.get('priority', 50)
                pir.metadata_ = new_pir_dict.get('metadata', {})
                pir.updated_at = datetime.now(timezone.utc)
                
                session.add(pir)
                logger.info(f"Updated P-IR {pir.id}")
            else:
                logger.info(f"Would update P-IR {pir.id} (dry run)")
        
        if not args.dry_run:
            # Commit the changes
            session.commit()
            logger.info("Migration completed successfully")
        else:
            logger.info("Dry run completed successfully (no changes made)")
    
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()

if __name__ == "__main__":
    main()

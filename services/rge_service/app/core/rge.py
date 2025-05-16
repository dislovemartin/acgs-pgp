import asyncio
import json
import logging
from typing import List, Optional

from fastapi import Depends, HTTPException
from kafka import KafkaConsumer
import httpx

from .config import settings
from ....common.schemas.pir import PIR
from ..engine.policy_evaluator import PolicyEvaluator

logger = logging.getLogger(__name__)

# Global policy evaluator instance
_policy_evaluator: Optional[PolicyEvaluator] = None

async def get_policy_evaluator() -> PolicyEvaluator:
    """Dependency to get the policy evaluator instance."""
    global _policy_evaluator
    if _policy_evaluator is None:
        _policy_evaluator = PolicyEvaluator()
        await update_policies()
    return _policy_evaluator

async def update_policies():
    """Fetch and update policies from the Policy Service."""
    global _policy_evaluator
    
    if _policy_evaluator is None:
        _policy_evaluator = PolicyEvaluator()
    
    try:
        async with httpx.AsyncClient() as client:
            # Fetch active policies from the Policy Service
            response = await client.get(
                f"{settings.POLICY_SERVICE_URL}/policies/",
                params={"status": "active"}
            )
            response.raise_for_status()
            
            policies_data = response.json()
            policies = [PIR(**policy) for policy in policies_data]
            
            # Update the evaluator with the latest policies
            _policy_evaluator.update_policies(policies)
            logger.info(f"Updated policies: {len(policies)} active policies loaded")
            
    except Exception as e:
        logger.error(f"Failed to update policies: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update policies: {str(e)}"
        )

async def start_policy_updater():
    """Background task to periodically update policies."""
    while True:
        try:
            await update_policies()
        except Exception as e:
            logger.error(f"Error in policy updater: {str(e)}")
        
        # Wait for the next update interval
        await asyncio.sleep(settings.POLICY_UPDATE_INTERVAL)

def setup_kafka_consumer():
    """Set up Kafka consumer for real-time policy updates."""
    consumer = KafkaConsumer(
        settings.KAFKA_POLICY_UPDATES_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    return consumer

async def process_kafka_messages():
    """Process Kafka messages for real-time policy updates."""
    consumer = setup_kafka_consumer()
    
    for message in consumer:
        try:
            # When we receive a policy update, refresh all policies
            if message.topic == settings.KAFKA_POLICY_UPDATES_TOPIC:
                logger.info("Received policy update event, refreshing policies...")
                await update_policies()
                
        except Exception as e:
            logger.error(f"Error processing Kafka message: {str(e)}")
            continue

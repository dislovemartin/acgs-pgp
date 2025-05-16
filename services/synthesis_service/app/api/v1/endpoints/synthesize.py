from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
import uuid
from datetime import datetime, timezone
import sys
import os
import json

from ....core.config import settings
from ....services.llm_service import LLMService
from ....services.kafka_producer import KafkaProducerService
from ....schemas.pir import (
    PolicySynthesisRequest,
    PolicySynthesisResponse
)
# Import the common PIR schema
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../')))
from common.schemas.pir import PIR
from ....models.policy import PolicyModel
from ....db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/synthesize",
    response_model=PolicySynthesisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Synthesize a policy from natural language intent",
    description="""
    Generate a policy (PIR) from a natural language description of the desired policy.
    The generated policy will be in draft status and can be reviewed before activation.
    """
)
async def synthesize_policy(
    request: PolicySynthesisRequest,
    db = Depends(get_db)
) -> PolicySynthesisResponse:
    """
    Generate a policy from natural language intent using an LLM.
    """
    try:
        # Initialize the LLM service
        llm_service = LLMService()

        # Generate the policy using the LLM
        response = await llm_service.synthesize_policy(request)

        # Save the generated policy to the database
        policy_data = response.policy.dict()
        policy_data["id"] = str(uuid.uuid4())
        policy_data["created_at"] = datetime.now(timezone.utc)
        policy_data["updated_at"] = datetime.now(timezone.utc)

        # Create the policy in the database
        db_policy = PolicyModel(**policy_data)
        db.add(db_policy)
        db.commit()
        db.refresh(db_policy)

        # Update the response with the database ID
        response.policy.id = db_policy.id

        # Send policy creation event to Kafka
        try:
            kafka_producer = KafkaProducerService(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                topic=settings.KAFKA_POLICY_UPDATES_TOPIC
            )

            event_data = {
                "event_type": "policy_created",
                "policy": response.policy.dict(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            kafka_producer.send_message(
                key=str(db_policy.id),
                value=event_data
            )

            logger.info(f"Sent policy_created event for policy {db_policy.id} to Kafka")
        except Exception as e:
            logger.error(f"Failed to send policy creation event to Kafka: {str(e)}")
            # Continue even if Kafka send fails

        return response

    except Exception as e:
        logger.error(f"Error in policy synthesis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to synthesize policy: {str(e)}"
        )

@router.get(
    "/synthesize/examples",
    response_model=List[dict],
    summary="Get example policy synthesis requests",
    description="Get a list of example policy synthesis requests for demonstration purposes."
)
async def get_synthesis_examples() -> List[dict]:
    """
    Get example policy synthesis requests.
    """
    examples = [
        {
            "intent": "Prevent sharing of personally identifiable information (PII)",
            "context": {
                "domain": "customer service",
                "regulations": ["GDPR", "CCPA"]
            },
            "constraints": [
                "Must detect and handle various PII formats (SSN, credit cards, etc.)",
                "Should log PII detection events for auditing purposes"
            ]
        },
        {
            "intent": "Ensure all financial advice includes appropriate disclaimers",
            "context": {
                "domain": "financial services",
                "regulations": ["FINRA", "SEC"]
            },
            "constraints": [
                "Must include standard investment disclaimers",
                "Should require human review for complex financial advice"
            ]
        },
        {
            "intent": "Prevent generation of harmful or offensive content",
            "context": {
                "domain": "general",
                "content_categories": ["hate_speech", "violence", "adult_content"]
            },
            "constraints": [
                "Must be culturally sensitive",
                "Should provide clear feedback when content is blocked"
            ]
        }
    ]

    return examples

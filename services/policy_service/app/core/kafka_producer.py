from kafka import KafkaProducer
import json
from datetime import datetime, timezone
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)
producer = None

def get_kafka_producer():
    """
    Initialize and return a Kafka producer singleton.
    """
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Kafka producer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            # Handle error appropriately, maybe raise or return None
    return producer

def send_policy_update_event(policy_data: dict, event_type: str):
    """
    Send a policy update event to Kafka.
    
    Args:
        policy_data: The policy data to send
        event_type: Type of event (policy_created, policy_updated, policy_deleted)
    """
    kafka_producer = get_kafka_producer()
    if kafka_producer:
        try:
            event = {
                "event_type": event_type,  # "policy_created", "policy_updated", "policy_deleted"
                "policy": policy_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            kafka_producer.send(settings.KAFKA_POLICY_UPDATES_TOPIC, value=event)
            kafka_producer.flush()  # Ensure message is sent
            logger.info(f"Sent {event_type} event for policy {policy_data.get('policy_id')}")
        except Exception as e:
            logger.error(f"Failed to send policy update event to Kafka: {e}")

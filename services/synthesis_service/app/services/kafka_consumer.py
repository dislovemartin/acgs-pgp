import json
import logging
from typing import Callable, Optional
from common.kafka import Consumer

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    """
    Service for consuming messages from Kafka topics.
    """
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str):
        """
        Initialize the Kafka consumer service.
        
        Args:
            bootstrap_servers: Comma-separated list of Kafka bootstrap servers
            topic: Default topic to consume messages from
            group_id: Consumer group ID
        """
        self.bootstrap_servers = bootstrap_servers
        self.default_topic = topic
        self.group_id = group_id
        
    def consume_messages(self, callback: Callable, topic: str = None, max_messages: Optional[int] = None):
        """
        Consume messages from a Kafka topic and process them with the provided callback.
        
        Args:
            callback: Function to call for each message
            topic: Optional topic override (default: use the topic specified at initialization)
            max_messages: Optional maximum number of messages to consume before returning
        """
        try:
            # Use the shared Consumer from common.kafka
            consumer = Consumer(
                bootstrap_servers=self.bootstrap_servers,
                topic=topic or self.default_topic,
                group_id=self.group_id
            )
            
            logger.info(f"Starting to consume messages from topic '{topic or self.default_topic}'")
            consumer.consume(callback, max_messages)
            
        except Exception as e:
            logger.error(f"Error consuming messages from Kafka: {str(e)}")
            raise

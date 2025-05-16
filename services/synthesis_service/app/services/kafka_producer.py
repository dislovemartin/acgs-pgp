import logging
from common.kafka import Producer
from ..core.config import settings

logger = logging.getLogger(__name__)

class KafkaProducerService:
    """
    Service for sending messages to Kafka topics.
    """
    def __init__(self, bootstrap_servers: str, topic: str):
        """
        Initialize the Kafka producer service.
        
        Args:
            bootstrap_servers: Comma-separated list of Kafka bootstrap servers
            topic: Default topic to send messages to
        """
        self.bootstrap_servers = bootstrap_servers
        self.default_topic = topic
        self.producer = None
        
    def send_message(self, key: str, value: dict, topic: str = None) -> bool:
        """
        Send a message to a Kafka topic.
        
        Args:
            key: Message key
            value: Message value (will be serialized to JSON)
            topic: Optional topic override (default: use the topic specified at initialization)
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        try:
            # Use the shared Producer from common.kafka
            producer = Producer(
                bootstrap_servers=self.bootstrap_servers,
                topic=topic or self.default_topic
            )
            
            result = producer.send(key=key, value=value)
            producer.close()
            
            if result:
                logger.info(f"Successfully sent message with key '{key}' to topic '{topic or self.default_topic}'")
            else:
                logger.error(f"Failed to send message with key '{key}' to topic '{topic or self.default_topic}'")
                
            return result
            
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {str(e)}")
            return False

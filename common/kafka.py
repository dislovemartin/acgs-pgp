import json
import logging
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

class Producer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers.split(','),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8')
        )

    def send(self, key: str, value: dict) -> bool:
        try:
            fut = self.producer.send(self.topic, key=key, value=value)
            fut.get(timeout=10)
            self.producer.flush()
            return True
        except (KafkaError, Exception) as e:
            logger.error(f"Kafka send error: {e}")
            return False

    def close(self):
        try:
            self.producer.close()
        except Exception:
            pass

class Consumer:
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers.split(','),
            group_id=group_id,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    def consume(self, handler, max_messages: int = None):
        count = 0
        try:
            for msg in self.consumer:
                try:
                    handler(msg.value)
                except Exception as e:
                    logger.error(f"Handler error: {e}")
                count += 1
                if max_messages is not None and count >= max_messages:
                    break
        finally:
            self.consumer.close()

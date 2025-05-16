import pytest
import json
from unittest.mock import patch, MagicMock, call
from kafka.errors import KafkaError
from app.services.kafka_producer import KafkaProducerService
from app.services.kafka_consumer import KafkaConsumerService

# Test data
TEST_TOPIC = "test-topic"
TEST_GROUP_ID = "test-group"
TEST_BOOTSTRAP_SERVERS = "localhost:9092"
TEST_MESSAGE = {"key": "test-key", "value": {"test": "data"}}

# Kafka Producer Tests

def test_kafka_producer_send_message_success():
    """Test successful message sending with Kafka producer."""
    with patch('kafka.KafkaProducer') as mock_producer_class:
        # Setup mock producer
        mock_producer = MagicMock()
        mock_future = MagicMock()
        mock_future.get.return_value = MagicMock()
        mock_producer.send.return_value = mock_future
        mock_producer_class.return_value = mock_producer
        
        # Create producer service
        producer = KafkaProducerService(
            bootstrap_servers=TEST_BOOTSTRAP_SERVERS,
            topic=TEST_TOPIC
        )
        
        # Send message
        result = producer.send_message(
            key=TEST_MESSAGE["key"],
            value=TEST_MESSAGE["value"]
        )
        
        # Assertions
        assert result is True
        mock_producer.send.assert_called_once_with(
            TEST_TOPIC,
            key=bytes(TEST_MESSAGE["key"], 'utf-8'),
            value=json.dumps(TEST_MESSAGE["value"]).encode('utf-8')
        )
        mock_producer.flush.assert_called_once()
        mock_producer.close.assert_called_once()

def test_kafka_producer_send_message_with_custom_topic():
    """Test sending message to a custom topic."""
    custom_topic = "custom-topic"
    
    with patch('kafka.KafkaProducer') as mock_producer_class:
        # Setup mock producer
        mock_producer = MagicMock()
        mock_future = MagicMock()
        mock_future.get.return_value = MagicMock()
        mock_producer.send.return_value = mock_future
        mock_producer_class.return_value = mock_producer
        
        # Create producer service
        producer = KafkaProducerService(
            bootstrap_servers=TEST_BOOTSTRAP_SERVERS,
            topic=TEST_TOPIC
        )
        
        # Send message to custom topic
        result = producer.send_message(
            key=TEST_MESSAGE["key"],
            value=TEST_MESSAGE["value"],
            topic=custom_topic
        )
        
        # Assertions
        assert result is True
        mock_producer.send.assert_called_once_with(
            custom_topic,
            key=bytes(TEST_MESSAGE["key"], 'utf-8'),
            value=json.dumps(TEST_MESSAGE["value"]).encode('utf-8')
        )

def test_kafka_producer_send_message_kafka_error():
    """Test handling of Kafka errors during message sending."""
    with patch('kafka.KafkaProducer') as mock_producer_class:
        # Setup mock producer to raise KafkaError
        mock_producer = MagicMock()
        mock_producer.send.side_effect = KafkaError("Kafka error")
        mock_producer_class.return_value = mock_producer
        
        # Create producer service
        producer = KafkaProducerService(
            bootstrap_servers=TEST_BOOTSTRAP_SERVERS,
            topic=TEST_TOPIC
        )
        
        # Send message and expect it to handle the error
        result = producer.send_message(
            key=TEST_MESSAGE["key"],
            value=TEST_MESSAGE["value"]
        )
        
        # Assertions
        assert result is False
        mock_producer.close.assert_called_once()

# Kafka Consumer Tests

def test_kafka_consumer_consume_messages():
    """Test consuming messages with Kafka consumer."""
    # Create test messages
    test_messages = [
        {"key": "key1", "value": {"test": "data1"}},
        {"key": "key2", "value": {"test": "data2"}},
    ]
    
    with patch('kafka.KafkaConsumer') as mock_consumer_class:
        # Setup mock consumer
        mock_consumer = MagicMock()
        mock_consumer.__iter__.return_value = [
            MagicMock(value=json.dumps(msg).encode('utf-8')) 
            for msg in test_messages
        ]
        mock_consumer_class.return_value = mock_consumer
        
        # Create consumer service
        consumer = KafkaConsumerService(
            bootstrap_servers=TEST_BOOTSTRAP_SERVERS,
            topic=TEST_TOPIC,
            group_id=TEST_GROUP_ID
        )
        
        # Create mock callback
        mock_callback = MagicMock()
        
        # Consume messages
        consumer.consume_messages(
            callback=mock_callback,
            max_messages=len(test_messages)
        )
        
        # Assertions
        assert mock_callback.call_count == len(test_messages)
        mock_consumer.subscribe.assert_called_once_with([TEST_TOPIC])
        mock_consumer.close.assert_called_once()

def test_kafka_consumer_with_custom_topic():
    """Test consuming messages from a custom topic."""
    custom_topic = "custom-topic"
    
    with patch('kafka.KafkaConsumer') as mock_consumer_class:
        # Setup mock consumer
        mock_consumer = MagicMock()
        mock_consumer.__iter__.return_value = []
        mock_consumer_class.return_value = mock_consumer
        
        # Create consumer service with default topic
        consumer = KafkaConsumerService(
            bootstrap_servers=TEST_BOOTSTRAP_SERVERS,
            topic=TEST_TOPIC,
            group_id=TEST_GROUP_ID
        )
        
        # Consume messages from custom topic
        consumer.consume_messages(
            callback=MagicMock(),
            topic=custom_topic,
            max_messages=1
        )
        
        # Assertions
        mock_consumer.subscribe.assert_called_once_with([custom_topic])

def test_kafka_consumer_error_handling():
    """Test error handling in Kafka consumer."""
    with patch('kafka.KafkaConsumer') as mock_consumer_class:
        # Setup mock consumer to raise an exception
        mock_consumer = MagicMock()
        mock_consumer.__iter__.side_effect = Exception("Consumer error")
        mock_consumer_class.return_value = mock_consumer
        
        # Create consumer service
        consumer = KafkaConsumerService(
            bootstrap_servers=TEST_BOOTSTRAP_SERVERS,
            topic=TEST_TOPIC,
            group_id=TEST_GROUP_ID
        )
        
        # Consume messages and expect exception to be propagated
        with pytest.raises(Exception, match="Consumer error"):
            consumer.consume_messages(
                callback=MagicMock(),
                max_messages=1
            )
        
        # Assert consumer was closed
        mock_consumer.close.assert_called_once()

def test_kafka_consumer_message_processing_error():
    """Test handling of message processing errors."""
    # Create test message with invalid JSON
    invalid_message = b'invalid json'
    
    with patch('kafka.KafkaConsumer') as mock_consumer_class:
        # Setup mock consumer
        mock_consumer = MagicMock()
        mock_consumer.__iter__.return_value = [MagicMock(value=invalid_message)]
        mock_consumer_class.return_value = mock_consumer
        
        # Create consumer service
        consumer = KafkaConsumerService(
            bootstrap_servers=TEST_BOOTSTRAP_SERVERS,
            topic=TEST_TOPIC,
            group_id=TEST_GROUP_ID
        )
        
        # Create mock callback
        mock_callback = MagicMock()
        
        # Consume messages - should handle the JSON decode error
        consumer.consume_messages(
            callback=mock_callback,
            max_messages=1
        )
        
        # Assert callback was not called due to JSON decode error
        mock_callback.assert_not_called()
        mock_consumer.close.assert_called_once()

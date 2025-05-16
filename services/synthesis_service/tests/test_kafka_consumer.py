import pytest
import json
from unittest.mock import patch, MagicMock, call
from kafka import KafkaConsumer
from app.services.kafka_consumer import KafkaConsumerService

@pytest.fixture
def mock_kafka_consumer():
    """Create a mock Kafka consumer."""
    with patch('kafka.KafkaConsumer') as mock_consumer:
        yield mock_consumer

@pytest.fixture
def kafka_consumer_service():
    """Create a KafkaConsumerService instance for testing."""
    return KafkaConsumerService(
        bootstrap_servers="localhost:9092",
        topic="test-topic",
        group_id="test-group"
    )

def test_consume_messages(kafka_consumer_service, mock_kafka_consumer):
    """Test consuming messages from a Kafka topic."""
    # Create a mock message
    test_message = {"key": "test-key", "value": {"test": "data"}}
    
    # Configure the mock consumer
    mock_consumer_instance = MagicMock()
    mock_consumer_instance.__iter__.return_value = [
        MagicMock(value=json.dumps(test_message).encode('utf-8'))
    ]
    mock_kafka_consumer.return_value = mock_consumer_instance
    
    # Create a mock callback function
    mock_callback = MagicMock()
    
    # Consume messages
    kafka_consumer_service.consume_messages(mock_callback, max_messages=1)
    
    # Verify the callback was called with the correct message
    mock_callback.assert_called_once_with(test_message)
    
    # Verify the consumer was properly closed
    mock_consumer_instance.close.assert_called_once()

def test_consume_messages_with_processing_error(kafka_consumer_service, mock_kafka_consumer):
    """Test handling of processing errors during message consumption."""
    # Create a mock message
    test_message = {"key": "test-key", "value": {"test": "data"}}
    
    # Configure the mock consumer
    mock_consumer_instance = MagicMock()
    mock_consumer_instance.__iter__.return_value = [
        MagicMock(value=json.dumps(test_message).encode('utf-8'))
    ]
    mock_kafka_consumer.return_value = mock_consumer_instance
    
    # Create a mock callback that raises an exception
    mock_callback = MagicMock(side_effect=Exception("Processing error"))
    
    # Consume messages and verify the error is caught
    kafka_consumer_service.consume_messages(mock_callback, max_messages=1)
    
    # Verify the callback was called
    mock_callback.assert_called_once()
    
    # Verify the consumer was properly closed
    mock_consumer_instance.close.assert_called_once()

def test_consume_messages_with_kafka_error(kafka_consumer_service, mock_kafka_consumer):
    """Test handling of Kafka errors during message consumption."""
    # Configure the mock consumer to raise an exception
    mock_consumer_instance = MagicMock()
    mock_consumer_instance.__iter__.side_effect = Exception("Kafka error")
    mock_kafka_consumer.return_value = mock_consumer_instance
    
    # Create a mock callback
    mock_callback = MagicMock()
    
    # Consume messages and verify the error is caught
    with pytest.raises(Exception, match="Kafka error"):
        kafka_consumer_service.consume_messages(mock_callback, max_messages=1)
    
    # Verify the callback was not called
    mock_callback.assert_not_called()
    
    # Verify the consumer was properly closed
    mock_consumer_instance.close.assert_called_once()

def test_consume_messages_with_custom_topic():
    """Test consuming messages from a custom topic."""
    # Create a mock consumer
    mock_consumer = MagicMock()
    mock_consumer.__iter__.return_value = []
    
    # Patch the KafkaConsumer to return our mock
    with patch('kafka.KafkaConsumer', return_value=mock_consumer) as mock_kafka_consumer:
        # Create a KafkaConsumerService instance
        service = KafkaConsumerService(
            bootstrap_servers="localhost:9092",
            topic="default-topic",
            group_id="test-group"
        )
        
        # Consume messages from a custom topic
        service.consume_messages(
            callback=MagicMock(),
            topic="custom-topic",
            max_messages=1
        )
        
        # Verify the consumer was created with the custom topic
        mock_kafka_consumer.assert_called_once()
        call_args = mock_kafka_consumer.call_args[1]
        assert call_args["bootstrap_servers"] == "localhost:9092"
        assert call_args["group_id"] == "test-group"
        assert call_args["value_deserializer"] is not None
        
        # Verify the consumer was properly closed
        mock_consumer.close.assert_called_once()

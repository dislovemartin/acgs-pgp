import pytest
from unittest.mock import patch, MagicMock
from kafka.errors import KafkaError
from app.services.kafka_producer import KafkaProducerService

@pytest.fixture
def mock_kafka_producer():
    """Create a mock Kafka producer."""
    with patch('kafka.KafkaProducer') as mock_producer:
        yield mock_producer

@pytest.fixture
def kafka_service():
    """Create a KafkaProducerService instance for testing."""
    return KafkaProducerService(
        bootstrap_servers="localhost:9092",
        topic="test-topic"
    )

def test_send_message_success(kafka_service, mock_kafka_producer):
    """Test successful message sending."""
    # Mock the producer's send method
    mock_future = MagicMock()
    mock_future.get.return_value = MagicMock()
    mock_kafka_producer.return_value.send.return_value = mock_future
    
    # Send a test message
    result = kafka_service.send_message("test-key", {"test": "data"})
    
    # Assert the message was sent successfully
    assert result is True
    mock_kafka_producer.return_value.send.assert_called_once()
    
    # Verify the producer was properly closed
    mock_kafka_producer.return_value.close.assert_called_once()

def test_send_message_kafka_error(kafka_service, mock_kafka_producer):
    """Test handling of Kafka errors during message sending."""
    # Mock the producer's send method to raise an exception
    mock_kafka_producer.return_value.send.side_effect = KafkaError("Kafka error")
    
    # Send a test message and expect an exception
    result = kafka_service.send_message("test-key", {"test": "data"})
    
    # Assert the message sending failed
    assert result is False
    mock_kafka_producer.return_value.send.assert_called_once()
    
    # Verify the producer was properly closed
    mock_kafka_producer.return_value.close.assert_called_once()

def test_send_message_serialization_error(kafka_service, mock_kafka_producer):
    """Test handling of serialization errors."""
    # Mock the producer's send method to raise a serialization error
    mock_kafka_producer.return_value.send.side_effect = TypeError("Serialization error")
    
    # Send a test message and expect an exception
    result = kafka_service.send_message("test-key", {"test": "data"})
    
    # Assert the message sending failed
    assert result is False
    mock_kafka_producer.return_value.send.assert_called_once()
    
    # Verify the producer was properly closed
    mock_kafka_producer.return_value.close.assert_called_once()

def test_send_message_with_custom_topic():
    """Test sending a message to a custom topic."""
    # Create a mock producer
    mock_producer = MagicMock()
    mock_future = MagicMock()
    mock_future.get.return_value = MagicMock()
    mock_producer.send.return_value = mock_future
    
    # Patch the KafkaProducer to return our mock
    with patch('kafka.KafkaProducer', return_value=mock_producer):
        # Create a KafkaProducerService instance
        service = KafkaProducerService(
            bootstrap_servers="localhost:9092",
            topic="default-topic"
        )
        
        # Send a message to a custom topic
        result = service.send_message(
            key="test-key",
            value={"test": "data"},
            topic="custom-topic"
        )
        
        # Assert the message was sent to the custom topic
        assert result is True
        mock_producer.send.assert_called_once_with(
            "custom-topic",
            key=b"test-key",
            value=b'{"test": "data"}'
        )
        
        # Verify the producer was properly closed
        mock_producer.close.assert_called_once()

# ACGS-PGP Common Utilities

This directory contains shared utilities and schemas used across the ACGS-PGP platform services.

## Modules

### Kafka

The `kafka.py` module provides standardized Kafka producer and consumer classes that can be used by all services in the platform. This ensures consistent handling of Kafka messages and error handling across the system.

#### Producer

```python
from common.kafka import Producer

# Create a producer
producer = Producer(
    bootstrap_servers="kafka:9092,localhost:9093",
    topic="my-topic"
)

# Send a message
producer.send(key="my-key", value={"data": "my-data"})

# Close the producer when done
producer.close()
```

#### Consumer

```python
from common.kafka import Consumer

# Define a message handler
def handle_message(message):
    print(f"Received message: {message}")

# Create a consumer
consumer = Consumer(
    bootstrap_servers="kafka:9092,localhost:9093",
    topic="my-topic",
    group_id="my-group"
)

# Consume messages
consumer.consume(handler=handle_message, max_messages=10)
```

### Schemas

The `schemas` directory contains Pydantic models that define the data structures used across the platform, ensuring consistency and type safety.

- `pir.py`: Policy Intermediate Representation (PIR) schema
- `constitution.py`: AI Constitution schema

## Usage

To use these common utilities in a service, make sure the common directory is in the Python path:

```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from common.kafka import Producer, Consumer
from common.schemas.pir import PIR
```

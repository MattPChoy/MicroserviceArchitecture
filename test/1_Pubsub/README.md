# Minimal Publisher/Consumer Example
- This Publisher/Consumer example demonstrates basic RabbitMQ functionality.
- The publisher sends a message to the queue, and the consumer receives it.
- The queue the publisher sends to is specified by the first argument provided.

```bash
python3 publisher.py queue_name
```

- The consumer receives from two queues, `queue1` and `queue2` and prints the received messages to STDOUT
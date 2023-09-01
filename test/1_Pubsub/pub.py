"""
This publisher publishes to a particular queue. It is run from the command line using the following
    command: python pub.py <queue-name>
"""
import sys
import pika
import logging

logging.basicConfig()

# Parse (fallback to localhost)
url = 'amqp://guest:guest@localhost/%2f'
params = pika.URLParameters(url)
params.socket_timeout = 5

connection = pika.BlockingConnection(params)  # Connect to CloudAMQP
channel = connection.channel()  # start a channel
q_name = sys.argv[1]
channel.queue_declare(queue=q_name, durable=True)  # Declare a queue
# send a message

print(f"Publishing to {q_name}")
while True:
    success = channel.basic_publish(exchange='', routing_key=f'{q_name}', body=bytes(input(f"{q_name}: "), 'utf-8'),
                                    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
    if success:
        print("Message sent")

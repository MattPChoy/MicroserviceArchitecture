"""
This Microservice is responsible for spamming the server with requests to process.
"""

import pika
import os
import random
import json

# read rabbitmq connection url from environment variable
amqp_url = os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/%2f')
url_params = pika.URLParameters(amqp_url)

# connect to rabbitmq
connection = pika.BlockingConnection(url_params)
chan = connection.channel()

# declare a new queue
# durable flag is set so that messages are retained
# in the rabbitmq volume even between restarts
chan.queue_declare(queue='intermediate-1', durable=True)

# publish a 100 messages to the queue
for i in range(10000):
    battery_name = random.choice(["Tesla Model S", "Tesla Model 3", "Tesla Model Y", "Tesla Model X", "Nissan Leaf"])

    data = {
        "event_type": "ADD_BATTERY",
        "capacity": random.randint(80, 150),
        "owner_id": random.randint(1, 100),
        "name": battery_name
    }

    chan.basic_publish(exchange='', routing_key='battery-management-service',
                       body=bytes(json.dumps(data), 'utf-8'), properties=pika.BasicProperties(delivery_mode=2))
    print("Produced the message")

chan.basic_publish(exchange='', routing_key="battery-management-service", body='{"event_type": "DUMP"}',
                   properties=pika.BasicProperties(delivery_mode=2))

# close the channel and connection
# to avoid program from entering with any lingering
# message in the queue cache
chan.close()
connection.close()

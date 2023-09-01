# example_publisher.py
import pika
import logging

logging.basicConfig()

# Parse (fallback to localhost)
url = 'amqp://guest:guest@localhost/%2f'
params = pika.URLParameters(url)
params.socket_timeout = 5

connection = pika.BlockingConnection(params)  # Connect to CloudAMQP
channel = connection.channel()  # start a channel
channel.queue_declare(queue='test')  # Declare a queue
# send a message

while True:
    channel.basic_publish(exchange='', routing_key='test', body=bytes(input("Send message to cons: "), 'utf-8'))

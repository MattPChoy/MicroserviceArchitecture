import pika
import os

connection = pika.BlockingConnection(
    pika.URLParameters(
        os.environ.get("AMQP_URL", "amqp://guest:guest@localhost/%2f")
    )
)
channel = connection.channel()
channel.queue_declare('test', durable=True)
try:
    while 1:
        channel.basic_publish(exchange='', routing_key='test',
                              body=b'Test')
except KeyboardInterrupt:
    connection.close()

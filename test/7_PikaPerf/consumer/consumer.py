import pika
import os

connection = pika.BlockingConnection(
    pika.URLParameters(
        os.environ.get("AMQP_URL", "amqp://guest:guest@localhost/%2f")
    )
)
channel = connection.channel()
channel.queue_declare('test', durable=True)

def on_consume(c, method_frame, header_frame, bod):
    c.basic_ack(delivery_tag=method_frame.delivery_tag)


channel.basic_consume('test', on_consume)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()

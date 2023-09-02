import pika
import time
import os

amqp_url = os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/%2f')
url_params = pika.URLParameters(amqp_url)

connection = pika.BlockingConnection(url_params)
read_chan = connection.channel()
read_chan.queue_declare(queue='intermediate-2', durable=True)


def receive_msg(ch, method, properties, body):
    res = body.decode('utf-8').split(' ').reverse().join(' ')
    print(res)


# to make sure the consumer receives only one message at a time
# next message is received only after acking the previous one
read_chan.basic_qos(prefetch_count=1)

# define the queue consumption
read_chan.basic_consume(queue='intermediate-2', on_message_callback=receive_msg)

print("Waiting to consume")
# start consuming
read_chan.start_consuming()

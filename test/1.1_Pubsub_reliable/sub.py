#!/usr/bin/env python
import pika

def receive():
    parameters = pika.ConnectionParameters(host='localhost')
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='raw_post', durable=True)
    method_frame, header_frame, body = channel.basic_get(queue='raw_post')

    # If method_frame is None, there are no messages left on the queue
    if method_frame is None or method_frame.NAME == 'Basic.GetEmpty':
        connection.close()
        exit(-1)
    else:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close()
        return body, method_frame.message_count


while 1:
    print(receive())

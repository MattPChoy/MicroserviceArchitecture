import json

import pika

# RabbitMQ connection setup
connection = pika.BlockingConnection(pika.URLParameters('amqp://rabbit_mq?connection_attempts=10&retry_delay=10'))
channel = connection.channel()
channel.queue_declare(queue='requests')
channel.queue_declare(queue='responses')


def process_request(ch, method, properties, body):
    _msg = body.decode()
    try:
        msg = json.loads(_msg)
    except json.decoder.JSONDecodeError as e:
        print(f"JSONDecodeError raised {e} {body}")
        return
    # Process the request here and generate a response
    response = json.dumps({
        "correlation_id": msg.get("correlation_id"),
        "message": msg.get("message")
    }).encode('utf-8')

    # Send the response to the RabbitMQ queue
    channel.basic_publish(exchange='', routing_key='responses', body=response)


# Consume requests from the queue and process them
channel.basic_consume(queue='requests', on_message_callback=process_request, auto_ack=True)

print("Microservice is waiting for requests...")
channel.start_consuming()

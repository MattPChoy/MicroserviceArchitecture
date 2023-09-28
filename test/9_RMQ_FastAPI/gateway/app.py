import uuid

from fastapi import FastAPI, HTTPException
import pika
import json

app = FastAPI()

# RabbitMQ connection setup
connection = pika.BlockingConnection(pika.URLParameters('amqp://rabbit_mq?connection_attempts=10&retry_delay=10'))
channel = connection.channel()
channel.queue_declare(queue='requests')
channel.queue_declare(queue='responses')


@app.get("/process/")
async def process_message(message: str):
    # Send the message to the RabbitMQ queue
    correlation_id = str(uuid.uuid4())
    body = {
        "correlation_id": correlation_id,
        "message": message
    }
    channel.basic_publish(exchange='', routing_key='requests', body=json.dumps(body).encode('utf-8'))

    # Wait for the response
    while True:
        method_frame, header_frame, body = channel.basic_get(queue='responses', auto_ack=False)
        if body is not None:
            try:
                response = json.loads(body.decode())
            except json.decoder.JSONDecodeError:
                print("Could not decode JSON response")
                return HTTPException(status_code=500, detail="Could not decode JSON response")
            break
    return response

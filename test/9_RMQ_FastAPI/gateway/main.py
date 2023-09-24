from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import threading
import aio_pika
import pika
import uuid
import json

app = FastAPI()

# Establish a connection to RabbitMQ
connection = pika.BlockingConnection(
    pika.URLParameters("amqp://rabbit_mq?connection_attempts=10&retry_delay=10"),

)
channel = connection.channel()

# Declare queues
channel.queue_declare(queue='battery-in')
channel.queue_declare(queue='battery-out')


def send_heartbeat():
    connection.process_data_events()


t = threading.Thread(target=send_heartbeat)


class BatteryMessage(BaseModel):
    message: str


@app.post("/battery")
async def send_battery_message(message: BatteryMessage):
    # Send a message to the battery-in queue
    channel.basic_publish(exchange='',
                          routing_key='battery-in',
                          body=message.message.encode('utf-8'))
    return {"message": "Message sent to battery-in queue"}


async def send_request_and_wait_for_response(battery_id, correlation_id):
    async with aio_pika.connect_robust("amqp://guest:guest@localhost/%2f") as connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("battery-in")
        response_queue = await channel.declare_queue("battery-out")

        request_message = {
            "correlation_id": correlation_id,
            "battery_id": battery_id
        }
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(request_message).encode('utf-8'),
                correlation_id=correlation_id,
                reply_to=response_queue.name
            ),
            routing_key=queue.name
        )

        async with response_queue.iterator() as queue_iter:
            async for message in queue_iter:
                if message.correlation_id == correlation_id:
                    response_message = message.body.decode('utf-8')
                    return {"message": response_message}


@app.get("/getBattery")
async def get_battery_message(battery_id: str = Query(..., description="Battery ID")):
    correlation_id = str(uuid.uuid4())
    print(f"Query received with battery_id: {battery_id} and correlation_id: {correlation_id}")

    response = await send_request_and_wait_for_response(battery_id, correlation_id)

    return response

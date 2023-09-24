from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika

app = FastAPI()

# Establish a connection to RabbitMQ
connection = pika.BlockingConnection(
    pika.URLParameters("amqp://rabbit_mq?connection_attempts=10&retry_delay=10"),

)
channel = connection.channel()

# Declare queues
channel.queue_declare(queue='battery-in')
channel.queue_declare(queue='battery-out')


class BatteryMessage(BaseModel):
    message: str


@app.post("/battery")
async def send_battery_message(message: BatteryMessage):
    # Send a message to the battery-in queue
    channel.basic_publish(exchange='',
                          routing_key='battery-in',
                          body=message.message.encode('utf-8'))
    return {"message": "Message sent to battery-in queue"}


@app.get("/getBattery")
async def get_battery_message():
    try:
        method_frame, header_frame, body = channel.basic_get(queue='battery-out')
        if method_frame:
            return {"message": body.decode('utf-8')}
        else:
            raise HTTPException(status_code=404, detail="No message available in battery-out queue")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve message from battery-out queue")

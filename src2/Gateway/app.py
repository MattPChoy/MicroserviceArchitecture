import os
import threading
import uuid
import socket
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika, json
import time


def get_local_ip():
    try:
        # Create a socket to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))  # Connect to a known external server (e.g., Google's DNS)
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error getting local IP address: {str(e)}")
        return None


app = FastAPI()

# RabbitMQ connection setup
AMQP_URL = os.environ.get("AMQP_URL", 'amqp://rabbit_mq?connection_attempts=10&retry_delay=10&heartbeat=20')
connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
channel = connection.channel()
channel.queue_declare(queue='status-in')
channel.queue_declare(queue='status-out')
channel.queue_declare(queue='battery-in')
channel.queue_declare(queue='battery-out')


def send_heartbeat():
    connection.process_data_events()


threading.Thread(target=send_heartbeat).start()
channel.queue_declare(queue='disco', durable=True)
channel.basic_publish(
    exchange='',
    routing_key='disco',
    body=json.dumps({
        # Retrieve name of class - this gets the implementing class' name
        "service_name": "Gateway",
        "timestamp": time.time(),
        "ip": get_local_ip()
    }).encode('utf-8'),
    properties=pika.BasicProperties(delivery_mode=2)
)


@app.post("/")
@app.get("/")
async def root():
    return "Hello World"


@app.get("/api/status")
async def status():
    """
    Send a call to the Disco service to get the status of all registered services.
    """
    global channel

    correlation_id = str(uuid.uuid4())
    body = {
        "correlation_id": correlation_id
    }
    try:
        channel.basic_publish(exchange='', routing_key='status-in', body=json.dumps(body).encode('utf-8'))
    except pika.exceptions.StreamLostError:
        # Try to connect again if the connection has been closed.
        connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
        channel = connection.channel()
        channel.basic_publish(exchange='', routing_key='status-in', body=json.dumps(body).encode('utf-8'))

    print("Sent message to status-in queue")

    while True:
        method_frame, header_frame, body = channel.basic_get(queue='status-out', auto_ack=False)
        if body is not None:
            try:
                response = json.loads(body.decode())
                if response["correlation_id"] == correlation_id:
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            except json.decoder.JSONDecodeError:
                print("Could not decode JSON response")
                return HTTPException(status_code=500, detail="Could not decode JSON response")
            break
    return response


@app.get("/api/batteries/")
async def get_batteries(id: int):
    global channel

    correlation_id = str(uuid.uuid4())
    body = {
        "type": "GET_BATTERY",
        "correlation_id": correlation_id,
        "battery_id": id
    }
    try:
        channel.basic_publish(exchange='', routing_key='battery-in', body=json.dumps(body).encode('utf-8'))
    except pika.exceptions.StreamLostError:
        # Try to connect again if the connection has been closed.
        connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
        channel = connection.channel()
        channel.basic_publish(exchange='', routing_key='battery-in', body=json.dumps(body).encode('utf-8'))
    print("Sent message to battery-in queue")
    while True:
        method_frame, header_frame, body = channel.basic_get(queue='battery-out', auto_ack=False)
        if body is not None:
            try:
                response = json.loads(body.decode())
                if response["correlation_id"] == correlation_id:
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            except json.decoder.JSONDecodeError:
                print("Could not decode JSON response")
                return HTTPException(status_code=500, detail="Could not decode JSON response")
            break
    return response


class Battery(BaseModel):
    name: str
    capacity: int
    charge: int


@app.post("/api/batteries")
async def post_batteries(battery: Battery):
    global channel

    correlation_id = str(uuid.uuid4())
    body = {
        "type": "ADD_BATTERY",
        "correlation_id": correlation_id,
        "name": battery.name,
        "capacity": battery.capacity,
        "charge": battery.charge
    }

    try:
        channel.basic_publish(exchange='', routing_key='battery-in', body=json.dumps(body).encode('utf-8'))
    except pika.exceptions.StreamLostError:
        # Try to connect again if the connection has been closed.
        connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
        channel = connection.channel()
        channel.basic_publish(exchange='', routing_key='battery-in', body=json.dumps(body).encode('utf-8'))
    print("Message sent to battery-in queue")

    while True:
        method_frame, header_frame, body = channel.basic_get(queue='battery-out', auto_ack=False)
        if body is not None:
            try:
                response = json.loads(body.decode())
                if response["correlation_id"] == correlation_id:
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            except json.decoder.JSONDecodeError:
                print("Could not decode JSON response")
                return HTTPException(status_code=500, detail="Could not decode JSON response")
            break
    return response

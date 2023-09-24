import os
import uuid
import json
import aio_pika  # Use aio-pika for asynchronous RabbitMQ connections
from fastapi import FastAPI, HTTPException
import logging
import asyncio
import uvicorn

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the AMQP URL from the environment variable
amqp_url = os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/%2f')


# Initialize an asynchronous connection to the RabbitMQ server
async def create_rabbitmq_connection():
    connection = await aio_pika.connect(amqp_url)
    return connection


# Declare the 'user-in' queue for sending requests to the user management microservice
async def declare_user_in_queue():
    connection = await create_rabbitmq_connection()
    channel = await connection.channel()
    await channel.declare_queue('user-in')


# Declare the 'user-out' queue for receiving responses from the user management microservice
async def declare_user_out_queue():
    connection = await create_rabbitmq_connection()
    channel = await connection.channel()
    await channel.declare_queue('user-out')


# Dictionary to store pending responses and correlate them with correlation ids
pending_responses = {}


# Function to handle incoming responses from the 'user-out' queue
async def process_user_response(message):
    async with message.process():
        correlation_id = message.correlation_id
        if correlation_id in pending_responses:
            # Update the response in the pending_responses dictionary
            pending_responses[correlation_id] = json.loads(message.body)
            logger.info(f"Received response for correlation_id: {correlation_id}")


# Set up a consumer for the 'user-out' queue to receive responses
async def setup_user_response_consumer():
    connection = await create_rabbitmq_connection()
    channel = await connection.channel()
    queue = await channel.get_queue('user-out')
    await queue.consume(process_user_response)


# Declare queues and set up consumers
async def startup_event():
    await declare_user_in_queue()
    await declare_user_out_queue()
    await setup_user_response_consumer()


@app.on_event("startup")
async def on_startup():
    await startup_event()


@app.get('/users')
async def get_user(uid: str):
    try:
        # Generate a correlation id using uuid
        correlation_id = str(uuid.uuid4())

        # Prepare the message with uid and correlation_id
        message = {
            'uid': uid,
            'correlation_id': correlation_id
        }

        connection = await create_rabbitmq_connection()

        # Create a channel and a message object
        channel = await connection.channel()
        message_obj = aio_pika.Message(
            json.dumps(message).encode('utf-8'),  # Encode message as bytes
            correlation_id=correlation_id
        )

        # Publish the message to the 'user-in' queue
        await channel.default_exchange.publish(
            message_obj,
            routing_key='user-in'
        )
        logger.info(f"Sent request for correlation_id: {correlation_id}")

        # Wait for the response with the corresponding correlation id
        while correlation_id not in pending_responses:
            await asyncio.sleep(0.1)

        response = pending_responses[correlation_id]

        # Remove the response from the pending_responses dictionary
        del pending_responses[correlation_id]
        logger.info(f"Returning response for correlation_id: {correlation_id}")

        return response

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def main():
    config = uvicorn.Config("api_gateway:app", port=5000, log_level="info")
    server = uvicorn.Server(config)
    logger.info("API Gateway is running...")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

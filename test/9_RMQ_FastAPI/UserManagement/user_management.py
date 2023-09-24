import os
import json
import pika
import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the AMQP URL from the environment variable
amqp_url = os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/%2f')

# Initialize a connection to the RabbitMQ server
connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
channel = connection.channel()

# Declare the 'user-in' queue for receiving requests from the API Gateway
channel.queue_declare(queue='user-in')

# Declare the 'user-out' queue for sending responses back to the API Gateway
channel.queue_declare(queue='user-out')

# PostgreSQL database configuration
db_config = {
    'dbname': 'exampledb',
    'user': 'docker',
    'password': 'docker',
    'host': 'postgres',  # Use the service name defined in docker-compose.yml
    'port': '5432'
}

# Create the 'users' table if it does not exist
try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        uid VARCHAR(255) NOT NULL,
        name VARCHAR(255),
        email VARCHAR(255)
    );
    """

    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

except Exception as e:
    logger.error(f"Error creating 'users' table: {str(e)}")


# Function to handle incoming messages from the 'user-in' queue
def process_user_message(ch, method, properties, body):
    try:
        # Parse the incoming message
        message = json.loads(body)

        # Extract the UID from the message
        uid = message.get('uid')
        correlation_id = message.get('correlation_id')
        service = message.get('service', 'User Management Microservice')

        logger.info(f"Received request from {service} for correlation_id: {correlation_id}")

        if uid:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Execute a SELECT query based on the UID
            select_query = "SELECT * FROM users WHERE uid = %s"
            cursor.execute(select_query, (uid,))

            # Fetch the result
            result = cursor.fetchone()

            # Close the database connection
            cursor.close()
            conn.close()

            # Prepare the response message
            response = {
                'uid': uid,
                'data': result,
                'correlation_id': correlation_id
            }

            # Publish the response to the 'user-out' queue
            channel.basic_publish(
                exchange='',
                routing_key='user-out',
                properties=pika.BasicProperties(
                    correlation_id=correlation_id,
                    delivery_mode=2
                ),
                body=json.dumps(response).encode('utf-8')  # Encode response as bytes
            )

            logger.info(f"Sent response to {service} for correlation_id: {correlation_id}")

    except Exception as e:
        logger.error(f"Error processing user message: {str(e)}")


# Start consuming messages from the 'user-in' queue
channel.basic_consume(queue='user-in', on_message_callback=process_user_message, auto_ack=False)

logger.info('User Management Microservice is waiting for messages. To exit, press Ctrl+C')

# Start the message consumption loop
try:
    channel.start_consuming()
except KeyboardInterrupt:
    pass

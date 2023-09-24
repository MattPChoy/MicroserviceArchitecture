import pika
import threading

# Establish a connection to RabbitMQ
connection = pika.BlockingConnection(pika.URLParameters("amqp://rabbit_mq?connection_attempts=10&retry_delay=10"))
channel = connection.channel()

# Declare queues
channel.queue_declare(queue='battery-in')
channel.queue_declare(queue='battery-out')


def send_heartbeat():
    connection.process_data_events()


t = threading.Thread(target=send_heartbeat)


def callback(ch, method, properties, body):
    # Handle the incoming message here
    response_message = f"Received and processed: {body.decode('utf-8')}"

    # Send the response message to battery-out queue
    channel.basic_publish(exchange='',
                          routing_key='battery-out',
                          body=response_message.encode('utf-8'))


# Set up a consumer to listen to battery-in queue
channel.basic_consume(queue='battery-in',
                      on_message_callback=callback,
                      auto_ack=True)

print("Battery Management Service is waiting for messages. To exit, press CTRL+C")
channel.start_consuming()

"""
The consumer is run from the command line using the syntax python cons.py, it
    consumes from both queue1 and queue2.
"""
import time

import pika
import signal
import sys
from multiprocessing import Process


def consume_channel(queue_name, callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name,
                          on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties,
                                                                                            body, queue_name),
                          auto_ack=True)
    print(f"Started consuming from {queue_name}")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        pass  # Continue to exit


def callback(ch, method, properties, body, queue_name):
    message = body.decode()
    print(f"{queue_name}:{message}")
    time.sleep(2)


def exit_program(signum, frame):
    print("Received Ctrl+C. Exiting.")
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_program)  # Register Ctrl+C handler

    queue_name1 = 'queue1'
    queue_name2 = 'queue2'

    process1 = Process(target=consume_channel, args=(queue_name1, callback))
    process2 = Process(target=consume_channel, args=(queue_name2, callback))

    process1.start()
    process2.start()

    try:
        process1.join()
        process2.join()
    except KeyboardInterrupt:
        print("Exiting gracefully.")

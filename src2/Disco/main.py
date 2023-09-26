import json
import logging
import os
import pika
from datetime import datetime
import threading


class Microservice:
    def __init__(self, amqp_url):
        self.DEFAULT_EXCHANGE = ''

        self.amqp_url = amqp_url
        self.connection = pika.BlockingConnection(
            pika.URLParameters(self.amqp_url)
        )
        self.channel = self.connection.channel()

        self._db = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")
        threading.Thread(target=self.send_heartbeat).start()

    def send_heartbeat(self):
        self.connection.process_data_events()

    def set_db(self, db):
        self._db = db

    def get_db(self):
        return self._db

    def listen(self, queue_name, callback, durable=True):
        self.channel.queue_declare(queue=queue_name, durable=durable)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)

    def add_write_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name, durable=True)

    def write(self, queue_name, message):
        # Queues are singleton so it is fine to re-declare a queue
        self.add_write_queue(queue_name)
        self.channel.basic_publish(
            exchange=self.DEFAULT_EXCHANGE,
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )


class Disco(Microservice):
    def __init__(self):
        super().__init__(amqp_url=os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/%2f'))
        self.services = {}

    def callback(self, channel, method, properties, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        _msg = body.decode('utf-8')
        try:
            msg = json.loads(_msg)
        except json.decoder.JSONDecodeError as e:
            logging.warning(f"JSONDecodeError: {e} {body}")
            return

        # TODO: Eventually fill this with some useful information
        self.services[msg["ip"]] = {
            "last_resp": msg["timestamp"],
            "ip": msg["ip"],
            "service_name": msg["service_name"],
        }
        print(f"Service Check-In {msg['service_name']}@{msg['ip']}")

    def start(self):
        self.listen("disco", self.callback)
        self.channel.start_consuming()


def format_timestamp(timestamp_str):
    try:
        if isinstance(timestamp_str, float):
            timestamp_str = datetime.utcfromtimestamp(timestamp_str).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
        return formatted_time
    except ValueError:
        return "Invalid Timestamp"


def handle_incoming_queries():
    print("Starting listener thread")

    def get_service_list(_channel, method, properties, body):
        _channel.basic_ack(delivery_tag=method.delivery_tag)

        _msg = body.decode('utf-8')
        try:
            msg = json.loads(_msg)
        except json.decoder.JSONDecodeError as e:
            logging.warning(f"JSONDecodeError: {e} {body}")
            return

        logging.info(f"Retrieved message from status-in queue {_msg}")

        reply_body = json.dumps({
            "correlation_id": msg["correlation_id"],
            "services": srv.services,
        }).encode('utf-8')
        channel.basic_publish(
            exchange='',
            routing_key='status-out',
            body=reply_body,
        )

    AMQP_URL = os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/%2f')
    connection = pika.BlockingConnection(
        pika.URLParameters(AMQP_URL)
    )
    channel = connection.channel()
    channel.basic_consume(queue='status-in', on_message_callback=get_service_list)
    channel.start_consuming()


if __name__ == "__main__":
    srv = Disco()
    srv.channel.queue_declare(queue='status-in')
    srv.channel.queue_declare(queue='status-out')

    t = (threading.Thread(target=handle_incoming_queries))
    t.start()
    srv.start()

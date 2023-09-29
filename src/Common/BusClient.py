import time
import json
import pika
import logging
import socket
from pika.exceptions import StreamLostError


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


class BusClient:
    def __init__(self, hostname="rabbit_mq"):
        self.hostname = hostname
        self.connection = self.get_connection()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")
        self.channel = self.connection.channel()
        # Hostname is used in the AMQP_URL and is the name of the docker container.

    def get_connection(self):
        """
        Retrieve a RMQ Connection
        """
        # AMQP_URL = os.environ.get("AMQP_URL", "amqp://rabbit_mq?connection_attempts=10&retry_delay=10")
        AMQP_URL = f"amqp://{self.hostname}?connection_attempts=10&retry_delay=10"
        return pika.BlockingConnection(pika.URLParameters(AMQP_URL))

    def publish(self, queue, msg: bytes):

        if type(msg) == dict:
            msg = json.dumps(msg).encode('utf-8')
        else:
            raise TypeError("msg parameter should be a bytestring")

        try:
            self.channel.basic_publish(exchange="", routing_key=queue, body=msg)
        except StreamLostError as e:
            self.logger.warning(f"StreamLostError: {e}")
            self.connection = self.get_connection()
            self.channel = self.connection.channel()
            self.channel.basic_publish(exchange="", routing_key=queue, body=msg)
        else:
            self.logger.info(f"Message published to {queue}")

    def send_discovery(self):
        data = {
            "ServiceName": type(self).__name__,
            "time": time.time(),
            "ip": get_local_ip(),
        }
        self.publish("discovery", json.dumps(data).encode('utf-8'))

import time
import json
import pika
import logging
import socket
import uuid
from .ServiceStatusType import ServiceStatusType
from pika.exceptions import StreamLostError


def get_local_ip():
    """
    Get the local IP address of the current device.
    :return String: The local IP address of the current device.
    """
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
        self.connection = self._get_connection()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")
        self.channel = self.connection.channel()
        # Hostname is used in the AMQP_URL and is the name of the docker container.

    def _get_connection(self):
        """
        Retrieve a message bus Connection object.
        :return BlockingConnection: A RMQ Connection object.
        """
        # AMQP_URL = os.environ.get("AMQP_URL", "amqp://rabbit_mq?connection_attempts=10&retry_delay=10")
        AMQP_URL = f"amqp://{self.hostname}?connection_attempts=10&retry_delay=10"
        return pika.BlockingConnection(pika.URLParameters(AMQP_URL))

    def publish(self, queue: str, msg: dict):
        """
        Publish a bytestring message to the message queue "queue".
        """

        assert type(msg) == dict, f"Message is of incorrect type. It should be a dict but is of type {type(msg)}"
        assert "correlation_id" in msg, f"Message must contain a correlation id"

        msg = json.dumps(msg).encode('utf-8')

        try:
            self.channel.basic_publish(exchange="", routing_key=queue, body=msg)
        except StreamLostError as e:
            self.logger.warning(f"StreamLostError: {e}")
            self.connection = self._get_connection()
            self.channel = self.connection.channel()
            self.channel.basic_publish(exchange="", routing_key=queue, body=msg)

    def send_discovery(self, service_name:str):
        """
        Send a message to the discovery queue, to tell the Discovery service (and the other services)
        that the current service is up and running.
        """

        assert service_name is not None, "Service name is undefined"
        data = {
            "name": service_name,
            "time": time.time(),
            "ip": get_local_ip(),
            "correlation_id": str(uuid.uuid4()),
            "type": ServiceStatusType.HEALTH_CHECK.value
        }
        self.publish("disco", data)

    def start(self):
        self.channel.start_consuming()

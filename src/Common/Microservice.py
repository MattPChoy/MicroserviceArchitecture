import logging
from BusClient import BusClient


class Microservice:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")
        self.bus_client = BusClient()
        self.name = type(self).__name__

    def start(self):
        # TODO: Tell Disco that we're alive.
        self.logger.info(f"Starting microservice {self.name}")



import logging
from Common.BusClient import BusClient


class Microservice:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.name = type(self).__name__
        logging.basicConfig(level=logging.INFO, format=f"[%(levelname)s@{self.name}] %(asctime)s: %(message)s")
        self.bus_client = BusClient()

    def start(self):
        # TODO: Tell Disco that we're alive.
        self.logger.info(f"Starting microservice {self.name}")

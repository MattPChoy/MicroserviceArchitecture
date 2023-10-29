import json
from json import JSONDecodeError

from Common.Microservice import Microservice
from Common.TaskQueue import TaskStatus, TaskQueue
from Common.ServiceStatusType import ServiceStatusType


class Disco(Microservice):
    def __init__(self):
        super().__init__()
        self.task_queue = TaskQueue()
        self.services = {}

    def add_service(self, service: dict):
        assert 'ip' in service, f"IP address not found in service definition dictionary. Key were {service.keys()}"
        self.services[service['ip']] = service

    def callback(self, channel, method, properties, body):
        """
        The message bus callback function that is executed when a message is sent to the disco queue. Handles the
        addition of a service.
        """

        _msg = body.decode('utf-8')

        try:
            msg = json.loads(_msg)
        except JSONDecodeError as error:
            self.logger.error(f"Error decoding message: {error}")
            self.bus_client.basic_nack(channel, method.delivery_tag)
            return

        assert "correlation_id" in msg, f"Service Request must contain correlation_id. Keys were {msg.keys()}"
        assert "type" in msg, f"Service request of unknown type received. {msg}"

        correlation_id = msg['correlation_id']

        try:
            request_type = ServiceStatusType(msg['type'])
        except ValueError:
            self.logger.error("Unknown service request type received")
            channel.basic_nack(method.delivery_tag)
            return

        if request_type == ServiceStatusType.HEALTH_CHECK:
            # Health-check/registration
            assert "ip" in msg, f"Service request must contain IP Address to be used as key. Keys were {msg.keys()}"
            # Add everything that's not the correlation_id - consider everything else to be part of the service definition
            self.add_service(
                {key: value for key, value in msg.items() if key != 'correlation_id'})
            self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED, payload={})
            self.logger.info(f"Added service {msg['name']}")
        elif request_type == ServiceStatusType.GET_STATUS:
            self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED, payload=self.services)

    def start(self):
        self.bus_client.start(queue="disco", callback=self.callback, auto_ack=False)


if __name__ == "__main__":
    srv = Disco()
    srv.start()

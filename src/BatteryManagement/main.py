import json
from json import JSONDecodeError

from Common.TaskQueue import TaskStatus, TaskQueue
from Common.BatteryRequestType import BatteryRequestType
from Common.Microservice import Microservice
from Gateway.models import BatteryTable


class BatteryManagement(Microservice):
    def __init__(self):
        super().__init__()
        self.battery_table = BatteryTable()
        self.task_queue = TaskQueue()
        self.bus_client.send_discovery()

    def callback(self, channel, method, properties, body):
        _msg = body.decode('utf-8')
        try:
            msg = json.loads(_msg)
            self.logger.warn(type(msg))
        except JSONDecodeError as error:
            self.logger.error(f"{error}")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        try:
            request_type = BatteryRequestType(msg.get("type", None))
        except ValueError:
            self.logger.error(f"Invalid request type: {msg.get('type', None)}")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        if request_type == BatteryRequestType.ADD_BATTERY:
            assert "owner" in msg, "Battery owner not defined"
            assert "name" in msg, "Battery name not defined"
            assert "capacity" in msg, "Battery capacity not defined"
            assert "charge" in msg, "Battery charge not defined"

            assert "correlation_id" in msg, "Correlation_id not defined"
            self.task_queue.update(correlation_id=msg["correlation_id"], status=TaskStatus.IN_PROGRESS)

            battery_id = self.battery_table.add(
                owner=msg["owner"],
                name=msg["name"],
                capacity=msg["capacity"],
                charge=msg["charge"]
            )

            assert type(battery_id) == int, "Battery ID returned from database table is not of integer type"
            response = {
                'battery_id': battery_id
            }
            self.task_queue.update(correlation_id=msg["correlation_id"], status=TaskStatus.SUCCEEDED,
                                   payload=response)
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self.bus_client.channel.queue_declare(queue="battery")
        self.bus_client.channel.basic_consume(queue="battery", on_message_callback=self.callback)
        self.bus_client.start()


if __name__ == "__main__":
    srv = BatteryManagement()
    srv.run()

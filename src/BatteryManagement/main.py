import json
from json import JSONDecodeError

from Common.TaskQueue import TaskStatus, TaskQueue
from Common.BatteryRequestType import BatteryRequestType
from Common.Microservice import Microservice
from Gateway.models import BatteryTable
from Gateway.models.Stations import StationsTable


class BatteryManagement(Microservice):
    def __init__(self):
        super().__init__()
        self.battery_table = BatteryTable()
        self.stations_table = StationsTable()
        self.task_queue = TaskQueue()
        self.bus_client.send_discovery(type(self).__name__)

    def add_battery(self, msg: dict):
        assert "owner" in msg, "Battery owner not defined"
        assert "name" in msg, "Battery name not defined"
        assert "capacity" in msg, "Battery capacity not defined"
        assert "charge" in msg, "Battery charge not defined"

        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.IN_PROGRESS)

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
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload=response)

    def get_battery_from_guid(self, msg: dict):
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        assert 'battery_id' in msg, "Battery ID not passed in request payload"

        if (battery := self.battery_table.get(msg['battery_id'])) is None:
            self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                                   payload={"battery_data": [], "desc": "No battery with this ID"})
            return
        elif battery is False:  # Some sort of SQL error
            self.logger.warn(f"Task failed as a result of SQL error (battery={battery})")
            self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.FAILED)
            return

        assert battery is not None, f"Battery to be returned is none (correlation_id={correlation_id}"
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload={"battery_data": dict(zip(self.battery_table.column_names, battery))})

    def get_batteries_owned_by(self, msg: dict):
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        if (batteries := self.battery_table.get_all_owned_by(msg['owner_id'])) is None:
            self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                                   payload={"battery_data": [], "desc": "No batteries corresponding to this owner id."})
            return
        elif batteries is False:  # Some sort of SQL error
            self.logger.warn(f"Task failed as a result of SQL error (battery={batteries})")
            self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.FAILED)
            return

        assert batteries is not None, f"Battery to be returned is none (correlation_id={correlation_id}"
        batteries = [dict(zip(self.battery_table.column_names, battery)) for battery in batteries]
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload={"battery_data": batteries})

    def update_battery_from_guid(self, msg):
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        assert 'id' in msg, f"Battery ID not passed in request payload. Keys were {msg.keys()}"

        # Temporarily add this to ensure that we prevent the propagation of null values through the system.
        assert 'owner' in msg, f"Battery owner not passed in request payload. Keys were {msg.keys()}"
        assert 'name' in msg, f"Battery name not passed in request payload. Keys were {msg.keys()}"
        assert 'capacity' in msg, f"Battery capacity not passed in request payload. Keys were {msg.keys()}"
        assert 'charge' in msg, f"Battery charge not passed in request payload. Keys were {msg.keys()}"

        # TODO: Make each of these optional?
        # TODO: Handle sql errors from the battery_table.update function
        self.battery_table.update(owner=msg['owner'], id=msg['id'], capacity=msg['capacity'], charge=msg['charge'],
                                  name=msg['name'])
        self.logger.info("Battery update succeeded.")
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED, payload={})

    def delete_battery_from_guid(self, msg):
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        assert 'id' in msg, f"Battery ID not passed in request payload. Keys were {msg.keys()}"

        self.battery_table.delete(msg['id'])
        self.logger.info(f"Battery delete succeeded (battery_id={msg['id']}, correlation_id={correlation_id})")
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED, payload={})

    def get_bss_station(self, msg):
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        assert "id" in msg, "Station ID not defined"
        station = self.stations_table.get(msg["id"])
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload={"station": station})

    def get_bss_stations(self, msg):
        """
        Retrieve all BSS stations registered to this deployment of the microservice application.
        :param msg:
        :return:
        """
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        stations = self.stations_table.get_all()
        column_names = [name for name in self.stations_table.column_names if stations is not 'active']
        stations = [dict(zip(column_names, station)) for station in stations]
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload={"stations": stations})

    def get_closest_bss_stations(self, msg):
        """
        Retrieve the n closest BSS stations to the specified location.
        :param msg:
        :return:
        """
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        assert "lat" in msg, "Latitude not defined"
        assert "lon" in msg, "Longitude not defined"
        assert "n" in msg, "Number of stations to retrieve not defined"

        stations = self.stations_table.get_n_closest(msg["lat"], msg["lon"], msg["n"])
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload={"stations": stations})

    def add_bss_station(self, msg):
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        assert "lat" in msg, "Latitude not defined"
        assert "lon" in msg, "Longitude not defined"
        assert "name" in msg, "Name not defined"

        station_id = self.stations_table.add(msg["lat"], msg["lon"], msg["name"])
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload={"station_id": station_id})

    def update_bss_station(self, msg):
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        assert "id" in msg, "Station ID not defined"
        assert "lat" in msg, "Latitude not defined"
        assert "lon" in msg, "Longitude not defined"
        assert "name" in msg, "Name not defined"

        self.stations_table.update(msg["id"], msg["lat"], msg["lon"], msg["name"])
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED, payload={})

    def delete_bss_station(self, msg):
        assert "correlation_id" in msg, "Correlation_id not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

        assert "id" in msg, "Station ID not defined"

        self.stations_table.delete(msg["id"])
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED, payload={})

    def reserve_battery(self, msg):
        assert "correlation_id" in msg, "Correlation_id not defined"
        assert "battery_id" in msg, "Battery ID not defined"
        assert "user_id" in msg, "User ID not defined"
        assert "duration" in msg, "Reservation duration not defined"
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id, TaskStatus.IN_PROGRESS)

    def callback(self, channel, method, properties, body):
        _msg = body.decode('utf-8')
        # channel.basic_ack(delivery_tag=method.delivery_tag)
        try:
            msg = json.loads(_msg)
        except JSONDecodeError as error:
            self.logger.error(f"Request type unknown {error}")
            # channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        try:
            request_type = BatteryRequestType(msg.get("type", None))
        except ValueError:
            self.logger.error(f"Invalid request type: {msg.get('type', None)}")
            # channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        self.logger.info(msg)
        if request_type == BatteryRequestType.ADD_BATTERY:
            self.add_battery(msg)
        elif request_type == BatteryRequestType.GET_BATTERY:
            # TODO: Maybe this should be separated into two different request types.
            if "owner_id" in msg:
                self.get_batteries_owned_by(msg)
            else:
                self.get_battery_from_guid(msg)
        elif request_type == BatteryRequestType.UPDATE_BATTERY:
            self.update_battery_from_guid(msg)
        elif request_type == BatteryRequestType.DELETE_BATTERY:
            self.delete_battery_from_guid(msg)
        elif request_type == BatteryRequestType.GET_STATION:
            self.get_bss_station(msg)
        elif request_type == BatteryRequestType.GET_STATIONS:
            self.get_bss_stations(msg)
        elif request_type == BatteryRequestType.GET_CLOSEST_STATIONS:
            self.get_closest_bss_stations(msg)
        elif request_type == BatteryRequestType.ADD_STATION:
            self.add_bss_station(msg)
        elif request_type == BatteryRequestType.UPDATE_STATION:
            self.update_bss_station(msg)
        elif request_type == BatteryRequestType.DELETE_STATION:
            self.delete_bss_station(msg)
        elif request_type == BatteryRequestType.BATTERY_RESERVATION:
            self.reserve_battery(msg)

    def start(self):
        self.bus_client.start(queue="battery", callback=self.callback, auto_ack=False)


if __name__ == "__main__":
    srv = BatteryManagement()
    srv.start()

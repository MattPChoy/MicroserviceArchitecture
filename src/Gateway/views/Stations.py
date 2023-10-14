"""
For Battery Swap Stations
"""

from fastapi import APIRouter, HTTPException
import logging

from Common.BatteryRequestType import BatteryRequestType
from Common.BusClient import BusClient
from Common.TaskQueue import TaskQueue
from Common.Utils import get_response
from models.Stations import Station

router = APIRouter(
    prefix="/api/v1/stations",
)

bus_client = BusClient()
task_queue = TaskQueue()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")


@router.get("/")
async def get_stations():
    correlation_id = task_queue.create_task()

    body = {
        "correlation_id": correlation_id,
        "type": BatteryRequestType.GET_STATIONS.value
    }

    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)


@router.get("/")
async def get_station(id: int):
    correlation_id = task_queue.create_task()

    body = {
        "correlation_id": correlation_id,
        "type": BatteryRequestType.GET_STATION.value,
        "id": id
    }

    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)


@router.post("/")
async def add_station(station: Station):
    correlation_id = task_queue.create_task()

    body = {
        "correlation_id": correlation_id,
        "type": BatteryRequestType.ADD_STATION.value,
        "lat": station.lat,
        "lon": station.lon,
        "name": station.name
    }

    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)


@router.put("/")
async def update_station(station: Station):
    if (id := station.id) is None:
        return HTTPException(422, "Station ID must be provided")
    correlation_id = task_queue.create_task()

    body = {
        "correlation_id": correlation_id,
        "type": BatteryRequestType.UPDATE_STATION.value,
        "id": id,
        "lat": station.lat,
        "lon": station.lon,
        "name": station.name
    }

    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)


@router.delete("/")
async def delete_station(id: int):
    correlation_id = task_queue.create_task()

    body = {
        "correlation_id": correlation_id,
        "type": BatteryRequestType.DELETE_STATION.value,
        "id": id
    }

    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)


@router.get("/closest")
async def get_closest_station(lat: float, lon: float, n: int = 1):
    correlation_id = task_queue.create_task()

    body = {
        "correlation_id": correlation_id,
        "type": BatteryRequestType.GET_CLOSEST_STATIONS.value,
        "lat": lat,
        "lon": lon,
        "n": n
    }

    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)


@router.get("/reservation")
async def get_reservation(station_id: int, uid: int):
    correlation_id = task_queue.create_task()

    body = {
        "correlation_id": correlation_id,
        "type": BatteryRequestType.BATTERY_RESERVATION.value,
        "station_id": station_id,
        "uid": uid
    }

    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache

from Common.BusClient import BusClient
from Common.TaskQueue import TaskQueue
from Common.BatteryRequestType import BatteryRequestType
from Common.Utils import get_response

import sys

sys.path.append("..")
# Ignore it, it's fine bro.
from models.Battery import Battery

router = APIRouter(
    prefix="/api/v1/battery",
)

bus_client = BusClient()
task_queue = TaskQueue()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(asctime)s: %(message)s")


@router.post("/")
async def add_battery(battery: Battery):
    correlation_id = task_queue.create_task()

    body = {
        "type": BatteryRequestType.ADD_BATTERY.value,
        "correlation_id": correlation_id,
        "owner": battery.owner,  # Battery owner UID
        "name": battery.name,
        "capacity": battery.capacity,
        "charge": battery.charge
    }
    bus_client.publish("battery", body)

    return await get_response(correlation_id=correlation_id)


@router.get("/")
@cache(expire=5000)
async def get_battery(id: int = None, owner_id: int = None):

    if id is None and owner_id is None:
        return HTTPException(422, "GET request must only contain one of battery ID or owner ID but contains none")
    if id is not None and owner_id is not None:
        return HTTPException(422, "GET request must only contain one of battery ID or owner ID but contains both")

    logger.info("Cache not hit?!")

    if id is not None:
        correlation_id = task_queue.create_task()

        body = {
            "type": BatteryRequestType.GET_BATTERY.value,
            "correlation_id": correlation_id,
            "battery_id": id
        }
        bus_client.publish("battery", body)
        return await get_response(correlation_id=correlation_id)

    # Handle the retrieval of all batteries owned by a particular owner
    correlation_id = task_queue.create_task()

    body = {
        "type": BatteryRequestType.GET_BATTERY.value,
        "correlation_id": correlation_id,
        "owner_id": owner_id
    }
    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)


@router.put("/")
async def update_battery(battery: Battery):
    correlation_id = task_queue.create_task()

    if battery.id is None:
        raise HTTPException(400, "PUT request must contain battery ID")

    # TODO: Do some validation here?

    body = {
        "type": BatteryRequestType.UPDATE_BATTERY.value,
        "correlation_id": correlation_id,
        "id": battery.id,
        "owner": battery.owner,
        "name": battery.name,
        "capacity": battery.capacity,
        "charge": battery.charge
    }

    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)


@router.delete("/")
async def delete_battery(battery_id: str):
    correlation_id = task_queue.create_task()
    body = {
        "type": BatteryRequestType.DELETE_BATTERY.value,
        "correlation_id": correlation_id,
        "id": battery_id,
    }
    bus_client.publish("battery", body)
    return await get_response(correlation_id=correlation_id)

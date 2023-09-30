import json
import time
import uuid
import logging
from fastapi import APIRouter, HTTPException
from Common.BusClient import BusClient
from Common.TaskQueue import TaskQueue, TaskStatus
from Common.BatteryRequestType import BatteryRequestType
from json import JSONDecodeError

import sys

sys.path.append("..")
# Ignore it, it's fine bro.
from models.Battery import Battery

router = APIRouter(
    prefix="/api/v1/battery",
)

rmq_client = BusClient()
task_queue = TaskQueue()

logger = logging.getLogger(__name__)
# TODO: Change back to logging.INFO level.
logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(asctime)s: %(message)s")


async def get_response(correlation_id: str):
    start_time = time.time()
    while True:
        if (_task := task_queue.get(correlation_id)) is None:
            logger.warning(f"Task details retrieved were Nonetype (correlation_id={correlation_id}).")
            continue

        try:
            task = json.loads(_task)
        except JSONDecodeError as error:
            logger.warning(f"Failed to decode task from redis {_task}: {error}")
            continue

        if task is None:
            continue

        if (task_status := task.get("status", None)) is None:
            continue

        task_status = TaskStatus(task_status)

        if time.time() - start_time > 30:
            raise HTTPException(status_code=500,
                                detail=f"Worker node took took long to respond (correlation_id={correlation_id})")
        if task_status in [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS]:
            # Keep blocking until the task has been processed by the worker
            continue
        elif task_status == TaskStatus.SUCCEEDED:
            if "payload" in task:
                return task["payload"]
            else:
                logger.warning("Deprecated. Task payload (from redis column) is empty.")
                return task
        elif task_status == TaskStatus.FAILED:
            raise HTTPException(status_code=400, detail=f"Task (correlation_id={correlation_id}) failed to complete")
        else:
            logger.warning("Timeout at time %s", time.time())
            raise HTTPException(status_code=400, detail=f"Request state {task_status.name} not implemented yet")


@router.post("/")
async def handle_root():
    return "Hello to the BatteryManagement World"


@router.post("/add")
async def add_battery(battery: Battery):
    correlation_id = str(uuid.uuid4())

    task_queue.add(correlation_id)

    body = {
        "type": BatteryRequestType.ADD_BATTERY.value,
        "correlation_id": correlation_id,
        "owner": battery.owner,  # Battery owner UID
        "name": battery.name,
        "capacity": battery.capacity,
        "charge": battery.charge
    }
    rmq_client.publish("battery", body)

    return await get_response(correlation_id=correlation_id)


@router.get("/get")
async def get_battery(battery_id: str):
    task_queue.add(battery_id)

    correlation_id = str(uuid.uuid4())
    body = {
        "type": BatteryRequestType.GET_BATTERY.value,
        "correlation_id": correlation_id,
        "battery_id": battery_id
    }
    rmq_client.publish("battery", body)

    return await get_response(correlation_id=correlation_id)

import json
import uuid
import logging
from fastapi import APIRouter, HTTPException
from Common.BusClient import BusClient
from Common.TaskQueue import TaskQueue, TaskStatus
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
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")


@router.post("/")
async def handle_root():
    return "Hello to the BatteryManagement World"


@router.post("/add")
async def add_battery(battery: Battery):
    correlation_id = str(uuid.uuid4())

    task_queue.add(correlation_id)

    body = {
        "type": "ADD_BATTERY",
        "correlation_id": correlation_id,
        "name": battery.name,
        "capacity": battery.capacity,
        "charge": battery.charge
    }

    rmq_client.publish("battery", body)

    while True:
        _task = task_queue.get(correlation_id)

        try:
            task = json.loads(_task)
        except JSONDecodeError as error:
            logger.warning(f"Failed to decode task from redis {_task}: {error}")
            continue

        logger.info(task)

        if task is None:
            continue

        if (task_status := task.get("status", None)) is None:
            continue

        task_status = TaskStatus(task_status)
        if task_status == TaskStatus.SUCCEEDED:
            return task.result
        elif task_status == TaskStatus.FAILED:
            raise HTTPException(status_code=400, detail="Task failed to complete")
        else:
            raise HTTPException(status_code=400, detail="Request state not implemented yet.")

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
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")


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
    logger.info(body)
    rmq_client.publish("battery", body)
    start_time = time.time()
    logger.info("Start processing request at time %s", start_time)

    while True:
        _task = task_queue.get(correlation_id)

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
            return task
        elif task_status == TaskStatus.FAILED:
            raise HTTPException(status_code=400, detail="Task failed to complete")
        else:
            logger.warning("Timeout at time %s", time.time())
            raise HTTPException(status_code=400, detail=f"Request state {task_status.name} not implemented yet")

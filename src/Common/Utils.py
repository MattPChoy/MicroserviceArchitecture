import time
from .TaskQueue import TaskQueue, TaskStatus
from fastapi import HTTPException
import json
from json import JSONDecodeError
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=f"[%(levelname)s] %(asctime)s: %(message)s")

task_queue = TaskQueue()


async def get_response(correlation_id: str):
    start_time = time.time()
    while True:
        if (_task := task_queue.get(correlation_id)) is None:
            # The loop may enter this branch several times before initial processing is finished and the
            # task is added to the redis queue
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

        if time.time() - start_time > 5:
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

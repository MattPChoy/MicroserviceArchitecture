import logging
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from Common.BusClient import BusClient
from Common.TaskQueue import TaskQueue
from Common.Utils import get_response
from Common.ServiceStatusType import ServiceStatusType

router = APIRouter(
    prefix="/api/v1/status"
)

bus_client = BusClient()
task_queue = TaskQueue()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(asctime)s: %(message)s")


@router.get("/")
@cache(expire=120)
async def get_service_status():
    correlation_id = task_queue.create_task()

    body = {
        "type": ServiceStatusType.GET_STATUS.value,
        "correlation_id": correlation_id
    }

    bus_client.publish("disco", body)
    return await get_response(correlation_id)

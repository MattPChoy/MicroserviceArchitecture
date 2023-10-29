import logging
from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache

from Common.BusClient import BusClient
from Common.TaskQueue import TaskQueue
from Common.UserRequestType import UserRequestType
from Common.Utils import get_response
from models.User import User

router = APIRouter(
    prefix="/api/v1/user",
)

bus_client = BusClient()
task_queue = TaskQueue()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(asctime)s: %(message)s")


@router.post("/")
async def add_user(user: User):
    correlation_id = task_queue.create_task()

    body = {
        "type": UserRequestType.ADD_USER.value,
        "correlation_id": correlation_id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "password": user.password,
        "region": user.region,
    }

    bus_client.publish("users", body)
    return await get_response(correlation_id)


@router.get("/")
@cache(expire=5000)
async def get_user(id: str):
    if id == "":
        raise HTTPException(status_code=400, detail="id cannot be empty")
    correlation_id = task_queue.create_task()

    body = {
        "type": UserRequestType.GET_USER.value,
        "correlation_id": correlation_id,
        "id": id,
    }

    bus_client.publish("users", body)
    return await get_response(correlation_id)


@router.put("/")
async def update_user(user: User):
    correlation_id = task_queue.create_task()

    body = {
        "type": UserRequestType.UPDATE_USER.value,
        "correlation_id": correlation_id,
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "password": user.password,
        "region": user.region,
    }

    bus_client.publish("users", body)
    return await get_response(correlation_id)


@router.delete("/")
async def delete_user(id: str):
    correlation_id = task_queue.create_task()

    if id == "":
        raise HTTPException(status_code=400, detail="id cannot be empty")

    body = {
        "type": UserRequestType.DELETE_USER.value,
        "correlation_id": correlation_id,
        "id": id,
    }

    bus_client.publish("users", body)
    return await get_response(correlation_id)

import uuid

import redis
from redis import Redis
import json
from enum import Enum


class TaskStatus(Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    SUCCEEDED = 2
    FAILED = 3


class TaskQueue:
    def __init__(self, redis_client: Redis = None):
        self.redis_client = redis_client or redis.Redis(host='taskqueue', port=6379, decode_responses=True)

    def create_task(self):
        correlation_id = str(uuid.uuid4())
        self.add(correlation_id)
        return correlation_id

    def add(self, correlation_id: str, payload=""):
        data = {
            "status": TaskStatus.NOT_STARTED.value,
            "payload": payload
        }
        return self.redis_client.set(correlation_id, json.dumps(data))

    def get(self, correlation_id: str):
        return self.redis_client.get(correlation_id)

    def update(self, correlation_id: str, status: [TaskStatus, int], payload: dict = None):
        assert type(status) in [TaskStatus, int]
        status = status if type(status) == int else status.value

        assert type(status) == int, f"status should be casted of type integer but is instead of type {type(status)}"
        assert payload is None or type(
            payload) == dict, f"payload should be of type dict but is instead of type {type(payload)}"
        payload = payload or dict()  # Set payload to an empty dictionary if it is None.

        return self.redis_client.set(correlation_id, json.dumps({"status": status, "payload": payload}))

    def remove(self, correlation_id: str):
        return self.redis_client.delete(correlation_id)

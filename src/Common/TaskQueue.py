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

    def add(self, correlation_id: str, payload=""):
        data = {
            "status": TaskStatus.NOT_STARTED.value,
            "payload": payload
        }
        return self.redis_client.set(correlation_id, json.dumps(data))

    def get(self, correlation_id: str):
        return self.redis_client.get(correlation_id)

    def update(self, correlation_id: str, status: [TaskStatus, int], payload=""):
        assert type(status) in [TaskStatus, int]
        status = status.value if status == type(TaskStatus) else status

        return self.redis_client.set(correlation_id, json.dumps({"status": status, "payload": payload}))

    def remove(self, correlation_id: str):
        return self.redis_client.delete(correlation_id)

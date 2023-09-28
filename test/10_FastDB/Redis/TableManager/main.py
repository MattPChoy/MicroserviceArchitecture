import redis
import json
from .TaskStatus import TaskStatus


class Tasks:
    def __init__(self, redis_client=None):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True) \
            if redis_client is None else redis_client

    def add(self, correlation_id, payload=""):
        return self.redis_client.set(correlation_id,
                                     json.dumps({"status": TaskStatus.NOT_STARTED.value, "payload": payload}))

    def get(self, correlation_id):
        return self.redis_client.get(correlation_id)

    def update(self, correlation_id, status, payload):
        if type(status) == TaskStatus:
            status = status.value
        assert type(status) == int

        return self.redis_client.set(correlation_id, json.dumps({"status": status, "payload": payload}))

    def delete(self, correlation_id):
        self.redis_client.delete(correlation_id)

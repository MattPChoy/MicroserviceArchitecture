import json
import time
import uuid
from http.client import HTTPException
from json import JSONDecodeError

from Common.TaskQueue import TaskStatus, TaskQueue
from Common.Microservice import Microservice
from Common.UserRequestType import UserRequestType


class Authentication(Microservice):
    def __init__(self):
        super().__init__()
        self.task_queue = TaskQueue()

    def get_user_credentials(self, username, correlation_id):
        start_time = time.time()
        while True:
            if (_task := self.task_queue.get(subtask_correlation_id)) is None:
                continue

            try:
                task = json.loads(_task)
            except JSONDecodeError as error:
                self.logger.warning(f"Failed to decode task from redis store {_task}: {error}")
                continue

            if task is None:
                continue

            if (task_status := task.get("status", None)) is None:
                continue

            task_status = TaskStatus(task_status)

            if time.time() - start_time > 5:
                self.task_queue.update(correlation_id, TaskStatus.FAILED, {"msg": "Task timed out"})
                self.logger.error(f"Retrieval of user credentials timed out with correlation id: {correlation_id}")
                return None, None

            if task_status == TaskStatus.FAILED:
                self.logger.error(f"Retrieval of username failed with correlation id: {correlation_id}")
                return None, None
            elif task_status == TaskStatus.SUCCEEDED:
                return task.get("username", None), task.get("password", None)

    def get_token(self, uid, password, correlation_id):
        subtask_correlation_id = self.task_queue.create_task()
        msg = {
            "request_type": UserRequestType.GET_CREDENTIALS,
            "uid": uid,
            "password": password,
            "correlation_id": uuid.uuid4()
        }

        self.bus_client.publish("users", msg)
        username, stored_password = self.get_user_credentials(uid, correlation_id)

        # Now check if the username and the stored password are the same.
        if password == stored_password:


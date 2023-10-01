import json
from json import JSONDecodeError

from Common.TaskQueue import TaskStatus, TaskQueue
from Common.UserRequestType import UserRequestType
from Common.Microservice import Microservice
from Gateway.models.User import UserTable


class UserManagement(Microservice):
    def __init__(self):
        super().__init__()
        self.users_table = UserTable()
        self.task_queue = TaskQueue()
        self.bus_client.send_discovery(type(self).__name__)

    def add_user(self, msg: dict):
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.IN_PROGRESS)

        for key in ["firstname", "lastname", "email", "password", "region"]:
            assert key in msg, f"{key} not defined"

        uid = self.users_table.add(firstname=msg['firstname'], lastname=msg['lastname'], email=msg['email'],
                                   password=msg['password'], region=msg['region'])
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload={'id': uid})

    def get_user(self, msg: dict):
        correlation_id = msg['correlation_id']
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.IN_PROGRESS)

        assert 'id' in msg, "User id not defined"

        user = self.users_table.get(msg['id'])
        payload = {}
        if user is None:
            payload['desc'] = f'no active user with id={msg["id"]}'
        else:
            payload['user'] = dict(zip(self.users_table.column_names, user))
        self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                               payload=payload)

    def update_user(self, msg: dict):
        correlation_id = msg['correlation_id']

        for key in ["id", "firstname", "lastname", "email", "password", "region"]:
            assert key in msg, f"{key} not defined"

        self.users_table.update(id=msg['id'], firstname=msg['firstname'], lastname=msg['lastname'], email=msg['email'],
                                password=msg['password'], region=msg['region'])
        self.task_queue.update(correlation_id, status=TaskStatus.SUCCEEDED, payload={})

    def delete_user(self, msg: dict):
        correlation_id = msg['correlation_id']
        hard = ('hard' in msg and msg['hard'] is True)
        self.users_table.delete(msg['id'], hard=hard)
        self.task_queue.update(correlation_id, status=TaskStatus.SUCCEEDED, payload={})

    def callback(self, channel, method, properties, body):
        _msg = body.decode('utf-8')
        try:
            msg = json.loads(_msg)
        except JSONDecodeError as error:
            self.logger.error(f"{error}")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        assert 'correlation_id' in msg, "Message does not contain correlation_id"
        correlation_id = msg['correlation_id']

        try:
            request_type = UserRequestType(msg['type'])
        except ValueError as error:
            self.logger.error(f"Request type unknown {error}")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        if request_type == UserRequestType.ADD_USER:
            self.add_user(msg)
        elif request_type == UserRequestType.GET_USER:
            self.get_user(msg)
        elif request_type == UserRequestType.UPDATE_USER:
            self.update_user(msg)
        elif request_type == UserRequestType.DELETE_USER:
            self.delete_user(msg)
        else:
            self.task_queue.update(correlation_id=correlation_id, status=TaskStatus.FAILED)
            self.logger.error("Unknown Request Type")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Check that the task has been marked as complete.
        _task = self.task_queue.get(correlation_id)
        try:
            _task = json.loads(_task)
        except JSONDecodeError as error:
            self.logger.error(f"Failed to decode task from redis {_task}: {error}")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        try:
            task_status = TaskStatus(_task['status'])
        except ValueError:
            self.logger.error(f"Invalid task state {_task}")
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        if task_status == TaskStatus.SUCCEEDED:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            self.logger.error(
                f"Task not in a completed state but execution has finished: {task_status}, {correlation_id}")

    def start(self):
        self.bus_client.channel.queue_declare(queue='users')
        self.bus_client.channel.basic_consume(queue='users', on_message_callback=self.callback)
        self.bus_client.start()


if __name__ == "__main__":
    srv = UserManagement()
    srv.start()

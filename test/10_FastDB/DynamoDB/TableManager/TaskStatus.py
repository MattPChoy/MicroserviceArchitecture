from enum import Enum


class TaskStatus(Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    SUCCEEDED = 2
    FAILED = 3

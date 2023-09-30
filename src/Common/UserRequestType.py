from enum import Enum


class UserRequestType(Enum):
    ADD_USER = 1
    GET_USER = 2
    UPDATE_USER = 3
    DELETE_USER = 4

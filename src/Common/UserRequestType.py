from enum import Enum


class UserRequestType(Enum):
    ADD_USER = 1
    GET_USER = 2
    UPDATE_USER = 3
    DELETE_USER = 4
    # An internal request type to get the credentials of a user for authentication verification.
    GET_CREDENTIALS = 5

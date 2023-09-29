from enum import Enum


class BatteryRequestType(Enum):
    """
    This Enum describes the different types of requests that can be sent to the battery microservice.
    """
    ADD_BATTERY = 1
    GET_BATTERY = 2
    UPDATE_BATTERY = 3
    DELETE_BATTERY = 4

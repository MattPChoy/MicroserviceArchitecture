from enum import Enum


class BatteryRequestType(Enum):
    """
    This Enum describes the different types of requests that can be sent to the battery microservice.
    """
    ADD_BATTERY = 1
    GET_BATTERY = 2
    UPDATE_BATTERY = 3
    DELETE_BATTERY = 4
    BATTERY_RESERVATION = 5
    GET_STATION = 6
    GET_STATIONS = 7
    GET_CLOSEST_STATIONS = 8
    ADD_STATION = 9
    UPDATE_STATION = 10
    DELETE_STATIONS = 11

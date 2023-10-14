import uuid

from pydantic import BaseModel


class Reservation(BaseModel):
    station_id: int
    user_id: int


class ReservationTable:
    def __init__(self, redis_client=None, redis=None):
        self.redis_client = redis_client or redis.Redis(host='reservation', port=6380, decode_responses=True)

    def create_reservation(self):
        reservation_id = str(uuid.uuid4())
        self.add(reservation_id)
        return reservation_id

    def add(self, reservation_id, payload=""):
        self.redis_client.set(reservation_id, )

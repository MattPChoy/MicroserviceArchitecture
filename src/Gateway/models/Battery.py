from pydantic import BaseModel


class Battery(BaseModel):
    name: str
    capacity: int
    charge: int

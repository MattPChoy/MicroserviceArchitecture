from fastapi import FastAPI
from views import BatteryManagement, UserManagement, Disco
from Common.BusClient import BusClient

import os

print(os.listdir(os.getcwd()), end="\n")

app = FastAPI()
bus_client = BusClient()
bus_client.send_discovery("Gateway")

# Register each of the microservices here.
app.include_router(BatteryManagement.router)
app.include_router(UserManagement.router)
app.include_router(Disco.router)

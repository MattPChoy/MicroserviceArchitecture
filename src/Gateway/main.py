from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from views import BatteryManagement, UserManagement, Disco
from Common.BusClient import BusClient

import os

print(os.listdir(os.getcwd()), end="\n")

app = FastAPI()
templates = Jinja2Templates(directory="./frontend/build/")

origins = ["http://localhost:5001", 'http://192.168.1.43:5001', "http://192.168.1.179", "http://192.168.1.179:5001",
           "http://192.168.1.179:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

bus_client = BusClient()
bus_client.send_discovery("Gateway")

# Register each of the microservices here.
app.include_router(BatteryManagement.router)
app.include_router(UserManagement.router)
app.include_router(Disco.router)

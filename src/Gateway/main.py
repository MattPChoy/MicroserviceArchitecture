from fastapi import FastAPI
from views import BatteryManagement, UserManagement

import os

print(os.listdir(os.getcwd()), end="\n")

app = FastAPI()

# Register each of the microservices here.
app.include_router(BatteryManagement.router)
app.include_router(UserManagement.router)

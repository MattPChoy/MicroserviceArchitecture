from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from views import BatteryManagement, UserManagement, Disco, Stations
from Common.BusClient import BusClient

app = FastAPI()

bus_client = BusClient()
bus_client.send_discovery("Gateway")

# Register each of the microservices here.
app.include_router(BatteryManagement.router)
app.include_router(UserManagement.router)
app.include_router(Disco.router)
app.include_router(Stations.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{str(request)}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://taskqueue:6379", decode_responses=False)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

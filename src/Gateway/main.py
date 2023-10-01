from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from views import BatteryManagement, UserManagement, Disco
from Common.BusClient import BusClient

app = FastAPI()

bus_client = BusClient()
bus_client.send_discovery("Gateway")

# Register each of the microservices here.
app.include_router(BatteryManagement.router)
app.include_router(UserManagement.router)
app.include_router(Disco.router)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://taskqueue:6379", decode_responses=False)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

from dudoxx.database.sqlite.database import setup_sqlite
from dudoxx.routes.api_key import router as api_key_router


async def setup_fastapi_ratelimiter():
    redis_connection = redis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)


async def lifespan(app: FastAPI):
    await setup_fastapi_ratelimiter()
    setup_sqlite()
    yield


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def pong():
    return {"ping": "pong!"}


app.include_router(api_key_router, prefix="/v1/api_key", tags=["api_key"])

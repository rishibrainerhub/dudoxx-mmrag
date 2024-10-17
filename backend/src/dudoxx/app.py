from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
import os

from dudoxx.database.sqlite.database import setup_sqlite
from dudoxx.routes import rag, drug, apikey, image, transcription, speech

redis_host = os.getenv("DDX_MMRAG_REDIS_HOST")
redis_port = os.getenv("DDX_MMRAG_REDIS_PORT")
redis_dns = f"redis://{redis_host}:{redis_port}"


async def setup_fastapi_ratelimiter():
    redis_connection = redis.from_url(redis_dns, encoding="utf-8", decode_responses=True)
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


app.include_router(apikey.router, prefix="/api/v1", tags=["api_key"])
app.include_router(drug.router, prefix="/api/v1", tags=["drug"])
app.include_router(image.router, prefix="/api/v1", tags=["image"])
app.include_router(transcription.router, prefix="/api/v1", tags=["transcription"])
app.include_router(speech.router, prefix="/api/v1", tags=["speach"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["rag"])

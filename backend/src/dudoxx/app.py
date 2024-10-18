from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
import os
from typing import List, Tuple, Optional, Dict
from functools import lru_cache
from pydantic_settings import BaseSettings
from contextlib import asynccontextmanager
from dudoxx.database.sqlite.database import setup_sqlite
from dudoxx.routes import rag, drug, apikey, image, transcription, speech


class Settings(BaseSettings):
    redis_host: str = os.getenv("DDX_MMRAG_REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("DDX_MMRAG_REDIS_PORT", 6379))
    redis_dns: str = f"redis://{redis_host}:{redis_port}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


async def setup_fastapi_ratelimiter() -> None:
    settings: Settings = get_settings()
    redis_connection: redis.Redis = redis.from_url(settings.redis_dns, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_fastapi_ratelimiter()
    setup_sqlite()
    yield


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/ping")
    async def pong() -> Dict[str, str]:
        return {"ping": "pong!"}

    api_v1_prefix: str = "/api/v1"
    routers: List[Tuple[APIRouter, str, Optional[str]]] = [
        (apikey.router, "api_key", None),
        (drug.router, "drug", None),
        (image.router, "image", None),
        (transcription.router, "transcription", None),
        (speech.router, "speech", None),
        (rag.router, "rag", "/rag"),
    ]

    for router, tag, additional_prefix in routers:
        prefix: str = f"{api_v1_prefix}{additional_prefix or ''}"
        app.include_router(router, prefix=prefix, tags=[tag])

    return app


# Create the FastAPI app
app: FastAPI = create_app()

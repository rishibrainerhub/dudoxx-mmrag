from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings and environment variables."""

    POSTGRES_USER: str = "dudoxx"
    POSTGRES_PASSWORD: str = "dudoxx"
    POSTGRES_DB: str = "dudoxx"
    POSTGRES_HOST: str = "pg_vector"
    POSTGRES_PORT: int = 5432
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    redis_host: str = os.getenv("DDX_MMRAG_REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("DDX_MMRAG_REDIS_PORT", 6379))
    redis_dns: str = f"redis://{redis_host}:{redis_port}"

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from functools import lru_cache
from contextlib import contextmanager
import logging
from typing import Generator

from dudoxx.database.pgvector.models import Base
from dudoxx.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_database_url() -> str:
    """Generate database URL from settings."""
    settings = get_settings()
    return f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"


# Create engine with basic pooling configuration
engine = create_engine(
    get_database_url(),
    pool_size=5,  # Reasonable default pool size
    max_overflow=10,
    pool_pre_ping=True,  # Helps detect stale connections
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session - compatible with FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def setup_pgvector() -> None:
    """Initialize database and create tables."""
    try:
        # Create pgvector extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

        # Create tables
        Base.metadata.create_all(engine)
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

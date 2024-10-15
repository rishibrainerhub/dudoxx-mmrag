from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from dudoxx.database.sqlite.models import Base

database_url = os.getenv("DATABASE_URL", default="sqlite:///./dudoxx.db")

engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_sqlite():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as ex:
        raise SystemExit(1) from ex

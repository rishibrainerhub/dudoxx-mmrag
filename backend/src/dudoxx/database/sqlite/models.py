from sqlalchemy import Column, String, DateTime
import datetime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class APIKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True, index=True)
    hashed_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now(tz=datetime.timezone.utc))
    last_used = Column(DateTime, nullable=True)

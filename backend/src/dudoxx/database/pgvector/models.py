from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()


class Document(Base):
    """Document model for storing text chunks and their embeddings."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    metadata_ = Column(JSONB, nullable=True)
    embedding = Column(Vector(1536))  # OpenAI embeddings are 1536 dimensions
    context_id = Column(String, nullable=True, index=True)

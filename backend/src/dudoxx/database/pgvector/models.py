from sqlalchemy import Column, Integer, Text, DateTime, func
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector


Base = declarative_base()


class Document(Base):
    """Document model for storing text and embeddings."""

    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    metadata_ = Column(Text, nullable=True)
    embedding = Column(Vector(1536), nullable=False)  # OpenAI embeddings are 1536 dimensions
    created_at = Column(DateTime, server_default=func.now())

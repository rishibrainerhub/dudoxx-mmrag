from typing import List, Optional, Dict, Any
from fastapi import Depends
from sqlalchemy.orm import Session
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document as LangchainDocument
from langchain.schema.retriever import BaseRetriever
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from dudoxx.database.pgvector.models import Document as DocumentModel
from dudoxx.config import Settings
from functools import lru_cache
from pydantic import Field
import json

from dudoxx.database.pgvector.database import get_db


@lru_cache()
def get_settings() -> Settings:
    return Settings()


class CustomRetriever(BaseRetriever):
    """Custom retriever that works with our VectorStore."""

    vectorstore: Any = Field(default=None, description="Vector store instance")
    search_kwargs: dict = Field(default_factory=lambda: {"k": 4})

    class Config:
        arbitrary_types_allowed = True

    async def _aget_relevant_documents(
        self,
        query: str,
    ) -> List[LangchainDocument]:
        """Get documents relevant to the query."""
        return await self.vectorstore.similarity_search(query, k=self.search_kwargs.get("k", 4))

    def _get_relevant_documents(
        self,
        query: str,
    ) -> List[LangchainDocument]:
        """Sync version of get_relevant_documents."""
        import asyncio

        return asyncio.run(self._aget_relevant_documents(query))


class VectorStore:
    """Vector store implementation using pgvector."""

    def __init__(
        self,
    ) -> None:
        """Initialize vector store with OpenAI embeddings."""
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.settings.OPENAI_API_KEY)
        self.db = next(get_db())

    def as_retriever(self, search_kwargs: Optional[dict] = None) -> CustomRetriever:
        """Return a retriever interface."""
        return CustomRetriever(vectorstore=self, search_kwargs=search_kwargs or {"k": 4})

    async def add_documents(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add documents to the vector store."""
        if metadatas is None:
            metadatas = [{}] * len(texts)

        embeddings = await self.embeddings.aembed_documents(texts)

        try:
            documents = [
                DocumentModel(content=text, metadata_=json.dumps(metadata) if metadata else None, embedding=embedding)
                for text, metadata, embedding in zip(texts, metadatas, embeddings)
            ]

            self.db.add_all(documents)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

    async def similarity_search(self, query: str, k: int = 4) -> List[LangchainDocument]:
        """Perform similarity search for the given query."""
        query_embedding = await self.embeddings.aembed_query(query)

        try:
            results = (
                self.db.query(DocumentModel)
                .order_by(DocumentModel.embedding.cosine_distance(query_embedding))
                .limit(k)
                .all()
            )

            return [
                LangchainDocument(page_content=doc.content, metadata=json.loads(doc.metadata_) if doc.metadata_ else {})
                for doc in results
            ]
        finally:
            self.db.close()

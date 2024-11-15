from typing import List, Optional, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document as LangchainDocument
from langchain.schema.retriever import BaseRetriever

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
    context_id: str = Field(default=None, description="ID for isolation context")

    class Config:
        arbitrary_types_allowed = True

    async def _aget_relevant_documents(
        self,
        query: str,
    ) -> List[LangchainDocument]:
        """Get documents relevant to the query."""
        return await self.vectorstore.similarity_search(
            query, k=self.search_kwargs.get("k", 4), context_id=self.context_id
        )

    def _get_relevant_documents(
        self,
        query: str,
    ) -> List[LangchainDocument]:
        """Sync version of get_relevant_documents."""
        import asyncio

        return asyncio.run(self._aget_relevant_documents(query))


class VectorStore:
    """Vector store implementation using pgvector with context isolation."""

    def __init__(self, default_context_id: Optional[str] = None) -> None:
        """Initialize vector store with OpenAI embeddings and optional default context ID."""
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.settings.OPENAI_API_KEY)
        self.db = next(get_db())
        self.default_context_id = default_context_id

    def as_retriever(self, search_kwargs: Optional[dict] = None, context_id: Optional[str] = None) -> CustomRetriever:
        """Return a retriever interface with optional context isolation."""
        return CustomRetriever(
            vectorstore=self, search_kwargs=search_kwargs or {"k": 4}, context_id=context_id or self.default_context_id
        )

    async def add_documents(
        self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, context_id: Optional[str] = None
    ) -> None:
        """Add documents to the vector store with context isolation."""
        if metadatas is None:
            metadatas = [{}] * len(texts)

        # Ensure each metadata dict has the context_id
        context_id = context_id or self.default_context_id
        if context_id:
            metadatas = [{**metadata, "context_id": context_id} for metadata in metadatas]

        embeddings = await self.embeddings.aembed_documents(texts)

        try:
            documents = [
                DocumentModel(
                    content=text,
                    metadata_=json.dumps(metadata) if metadata else None,
                    embedding=embedding,
                    context_id=context_id,
                )
                for text, metadata, embedding in zip(texts, metadatas, embeddings)
            ]

            self.db.add_all(documents)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

    async def similarity_search(
        self, query: str, k: int = 4, context_id: Optional[str] = None
    ) -> List[LangchainDocument]:
        """Perform similarity search for the given query within a specific context."""
        query_embedding = await self.embeddings.aembed_query(query)

        try:
            # Base query
            query = self.db.query(DocumentModel).order_by(DocumentModel.embedding.cosine_distance(query_embedding))

            # Add context filter if provided
            context_id = context_id or self.default_context_id
            if context_id:
                query = query.filter(DocumentModel.context_id == context_id)

            results = query.limit(k).all()

            return [
                LangchainDocument(page_content=doc.content, metadata=json.loads(doc.metadata_) if doc.metadata_ else {})
                for doc in results
            ]
        finally:
            self.db.close()

    async def delete_documents(self, context_id: str) -> None:
        """Delete all documents for a specific context ID."""
        try:
            self.db.query(DocumentModel).filter(DocumentModel.context_id == context_id).delete()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

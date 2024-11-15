from typing import List, Dict, Any, Optional
from dudoxx.pgvector_rag.vector_store import VectorStore
from dudoxx.pgvector_rag.rag import RAGSystem
from dudoxx.schemas.rag_pgvector import QuestionResponse
import asyncio
from docling.document_converter import DocumentConverter
from dudoxx.services.redis_service import RedisCacheService


class RAGService:
    """Service class for handling RAG operations with context isolation."""

    def __init__(self, default_context_id: Optional[str] = None):
        self.vector_store = VectorStore(default_context_id=default_context_id)
        self.rag_system = RAGSystem(self.vector_store)
        self._document_status = {}
        self.cache_service = RedisCacheService()

    async def process_document(self, file_path: str, task_id: str, context_id: Optional[str] = None) -> int:
        """
        Process a PDF document and store it in the vector store with context isolation.

        Args:
            file_path: Path to the PDF file
            task_id: ID for tracking processing status
            context_id: ID for isolating the document in its own context
        Returns:
            document ID
        """
        try:
            await self.cache_service.set(task_id, {"status": "Ingesting", "progress": 0})

            # Extract text from PDF
            texts = await asyncio.to_thread(self._extract_text_from_pdf, file_path)

            # Split text into chunks
            chunks = await asyncio.to_thread(self._chunk_text, texts)
            await self.cache_service.set(task_id, {"status": "vectorizing", "progress": 50})

            # Generate document ID
            doc_id = hash(f"{context_id}:{file_path}" if context_id else file_path)

            # Create metadata with context information
            metadatas = [
                {
                    "source": file_path,
                    "chunk": i,
                    "total_chunks": len(chunks),
                    "doc_id": doc_id,
                    "context_id": context_id,
                }
                for i in range(len(chunks))
            ]

            # Add to vector store with context isolation
            await self.vector_store.add_documents(texts=chunks, metadatas=metadatas, context_id=context_id)

            # Store status with context
            status_key = f"{context_id}:{doc_id}" if context_id else str(doc_id)
            self._document_status[status_key] = "processed"

            await self.cache_service.set(task_id, {"status": "Completed", "progress": 100})
            return doc_id

        except Exception as e:
            await self.cache_service.set(task_id, {"status": "Failed", "progress": 100, "error": str(e)})
            raise Exception(f"Error processing document: {str(e)}")

    async def get_answer(self, question: str, context_id: Optional[str] = None) -> QuestionResponse:
        """
        Get an answer for a question using the RAG system within a specific context.

        Args:
            question: The question to answer
            context_id: Optional context to restrict the search
        """
        try:
            # Update RAG system with context
            self.rag_system.context_id = context_id

            response = await self.rag_system.query(question)
            sources = [doc.metadata.get("source") for doc in response["source_documents"]]
            confidence_score = await asyncio.to_thread(self._calculate_confidence_score, response, context_id)

            return QuestionResponse(
                answer=response["answer"], sources=sources, confidence_score=confidence_score, context_id=context_id
            )

        except Exception as e:
            raise Exception(f"Error getting answer: {str(e)}")

    async def get_document_status(self, doc_id: int, context_id: Optional[str] = None) -> str:
        """
        Get the processing status of a document within a context.
        """
        status_key = f"{context_id}:{doc_id}" if context_id else str(doc_id)
        return self._document_status.get(status_key, "not_found")

    async def delete_context(self, context_id: str) -> None:
        """
        Delete all documents and embeddings for a specific context.
        """
        try:
            await self.vector_store.delete_documents(context_id)
            # Clean up document status entries for this context
            self._document_status = {
                k: v for k, v in self._document_status.items() if not k.startswith(f"{context_id}:")
            }
        except Exception as e:
            raise Exception(f"Error deleting context: {str(e)}")

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document.export_to_text()

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks of approximately equal size."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            word_size = len(word) + 1  # +1 for space
            if current_size + word_size > chunk_size:
                if current_chunk:  # Avoid empty chunks
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _calculate_confidence_score(self, response: Dict[str, Any], context_id: Optional[str] = None) -> float:
        """
        Calculate a confidence score based on the response and context.
        """
        sources = len(response.get("source_documents", []))
        if sources == 0:
            return 0.0

        # Calculate relevance score based on source documents
        source_scores = []
        for doc in response["source_documents"]:
            # Verify context match if context_id is provided
            if context_id and doc.metadata.get("context_id") != context_id:
                continue

            # Add your relevance scoring logic here
            content_length = len(doc.page_content)
            source_scores.append(min(content_length / 500, 1.0))

        if not source_scores:
            return 0.0

        avg_source_score = sum(source_scores) / len(source_scores)

        # Calculate answer quality score
        answer_length = len(response.get("answer", ""))
        answer_score = min(answer_length / 200, 1.0)

        # Weighted combination
        final_score = avg_source_score * 0.7 + answer_score * 0.3
        return round(final_score, 2)

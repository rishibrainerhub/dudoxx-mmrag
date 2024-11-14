from typing import List, Dict, Any
from dudoxx.pgvector_rag.vector_store import VectorStore
from dudoxx.pgvector_rag.rag import RAGSystem
from dudoxx.schemas.rag_pgvector import QuestionResponse
import asyncio
from docling.document_converter import DocumentConverter
from dudoxx.services.redis_service import RedisCacheService


class RAGService:
    """Service class for handling RAG operations."""

    def __init__(self):
        self.vector_store = VectorStore()
        self.rag_system = RAGSystem(self.vector_store)
        self._document_status = {}
        self.cache_service = RedisCacheService()

    async def process_document(self, file_path: str, task_id: str) -> int:
        """
        Process a PDF document and store it in the vector store.
        Returns the document ID.
        """
        try:
            await self.cache_service.set(task_id, {"status": "Ingesting", "progress": 0})
            # Extract text from PDF
            texts = await asyncio.to_thread(self._extract_text_from_pdf, file_path)

            # Split text into chunks
            chunks = await asyncio.to_thread(self._chunk_text, texts)
            await self.cache_service.set(task_id, {"status": "vectorizing", "progress": 50})
            # Add to vector store
            doc_ids = await self.vector_store.add_documents(
                texts=chunks,
                metadatas=[{"source": file_path, "chunk": i, "total_chunks": len(chunks)} for i in range(len(chunks))],
            )

            # Store status
            doc_id = hash(file_path)  # Simple hash-based ID
            self._document_status[doc_id] = "processed"
            await self.cache_service.set(task_id, {"status": "Completed", "progress": 100})
            return doc_id

        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")

    async def get_answer(self, question: str) -> QuestionResponse:
        """
        Get an answer for a question using the RAG system.
        """
        try:
            response = await self.rag_system.query(question)
            sources = [doc.metadata.get("source") for doc in response["source_documents"]]
            confidence_score = await asyncio.to_thread(self._calculate_confidence_score, response)

            return QuestionResponse(answer=response["answer"], sources=sources, confidence_score=confidence_score)

        except Exception as e:
            raise Exception(f"Error getting answer: {str(e)}")

    async def get_document_status(self, doc_id: int) -> str:
        """
        Get the processing status of a document.
        """
        return self._document_status.get(doc_id, "not_found")

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        """
        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document.export_to_text()  # here is the code change

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """
        Split text into chunks of approximately equal size.
        """
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

    def _calculate_confidence_score(self, response: Dict[str, Any]) -> float:
        """
        Calculate a confidence score based on the response.
        """
        sources = len(response.get("source_documents", []))
        if sources == 0:
            return 0.0

        # Calculate relevance score based on source documents
        source_scores = []
        for doc in response["source_documents"]:
            # Add your relevance scoring logic here
            content_length = len(doc.page_content)
            source_scores.append(min(content_length / 500, 1.0))

        avg_source_score = sum(source_scores) / len(source_scores)

        # Calculate answer quality score
        answer_length = len(response.get("answer", ""))
        answer_score = min(answer_length / 200, 1.0)

        # Weighted combination
        final_score = avg_source_score * 0.7 + answer_score * 0.3
        return round(final_score, 2)

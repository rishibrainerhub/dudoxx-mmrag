from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dudoxx.pgvector_rag.vector_store import VectorStore
from dudoxx.config import Settings
from functools import lru_cache


@lru_cache()
def get_settings() -> Settings:
    return Settings()


class RAGSystem:
    """RAG system implementation."""

    def __init__(self, vector_store: VectorStore) -> None:
        """Initialize RAG system with vector store and LLM."""
        self.vector_store = vector_store
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", api_key=get_settings().OPENAI_API_KEY)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            memory=self.memory,
            return_source_documents=True,
            output_key="answer",
        )

    async def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system with a question."""
        try:
            response = await self.chain.ainvoke({"question": question})
            return {"answer": response.get("answer"), "source_documents": response.get("source_documents")}
        except Exception as e:
            raise Exception(f"Error querying RAG system: {str(e)}")

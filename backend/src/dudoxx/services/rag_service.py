from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain.schema import Document
from langchain_core.callbacks import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain

from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableSequence

from dudoxx.schemas.rag import StructuredAnswer
from dudoxx.exceptions.rag_exceprions import RAGServiceError

load_dotenv()


class RAGService:
    def __init__(self) -> None:
        self.search = DuckDuckGoSearchAPIWrapper()
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.vector_store = FAISS.from_texts([""], self.embeddings)
        self.llm = ChatOpenAI(
            temperature=0, streaming=True, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.output_parser = PydanticOutputParser(pydantic_object=StructuredAnswer)

    async def search_and_store(self, query: str) -> None:
        try:
            search_results = self.search.results(query, max_results=5)
            documents = [
                Document(page_content=result["snippet"], metadata={"source": result["link"]})
                for result in search_results
            ]
            await self.vector_store.aadd_documents(documents)
        except Exception as e:
            raise RAGServiceError(f"Error in search_and_store: {str(e)}")

    async def get_answer(self, query: str) -> StructuredAnswer:
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(),
                return_source_documents=True,
                chain_type_kwargs={
                    "prompt": PromptTemplate(
                        template="Answer the following question based on the context provided. If you're not sure, say 'I don't know'.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer: ",
                        input_variables=["context", "question"],
                    )
                },
            )
            result = await qa_chain.ainvoke({"query": query})

            sources = self._extract_sources(result.get("source_documents", []))
            answer = result.get("result", "I don't have an answer for that question.")
            confidence = self._calculate_confidence(answer, sources)

            return StructuredAnswer(answer=answer, sources=sources, confidence=confidence)
        except Exception as e:
            print(f"Error in get_answer: {str(e)}")
            raise RAGServiceError(f"Error in get_answer: {str(e)}")

    async def get_conversational_answer(self, query: str) -> Dict[str, Any]:
        try:
            prompt = PromptTemplate(
                template="Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.\n\nContext: {context}\n\nQuestion: {query}\n\nHelpful Answer:",
                input_variables=["context", "query"],
            )

            history_aware_retriever = self.vector_store.as_retriever()

            retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=history_aware_retriever,
                return_source_documents=True,
                rephrase_question=True,
            )

            question_generator = RunnableSequence(
                RunnablePassthrough(),
                prompt,
                self.llm,
                StrOutputParser(),
            )
            result = await retrieval_chain.ainvoke(
                {
                    "question": query,
                    "chat_history": [],  # Add chat history here if available
                    "question_generator": question_generator,
                }
            )

            sources = self._extract_sources(result.get("source_documents", []))
            confidence = self._calculate_confidence(result["answer"], sources)

            return {"question": query, "answer": result["answer"], "sources": sources, "confidence": confidence}
        except Exception as e:
            raise RAGServiceError(f"Error in get_conversational_answer: {str(e)}")

    def _extract_sources(self, documents: List[Document]) -> List[str]:
        sources = []
        for doc in documents:
            if isinstance(doc.metadata, dict):
                source = doc.metadata.get("source") or doc.metadata.get("url") or "Unknown source"
            else:
                source = "Unknown source"
            sources.append(source)
        return sources

    def _calculate_confidence(self, answer: str, sources: List[str]) -> float:
        if not sources:
            return 0.0
        elif "I don't know" in answer:
            return 0.1
        else:
            return min(0.5 + (len(sources) * 0.1), 1.0)

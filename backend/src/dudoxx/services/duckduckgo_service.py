from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAI
from duckduckgo_search import DDGS
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
import json

from dudoxx.exceptions.openai_exceptions import handle_openai_api_error
from dudoxx.schemas.duckduckgo import DrugInfo, DiseaseInfo
from dudoxx.services.redis_service import RedisCacheService


class DuckDuckGOService:
    def __init__(self):
        self.ddg_search = DDGS()
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        self.llm = OpenAI(temperature=0)
        self.cache = RedisCacheService()

    async def _perform_search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        search_results = list(self.ddg_search.text(query, max_results=max_results))
        return [{"snippet": result["body"], "link": result["href"]} for result in search_results]

    async def _create_vector_db(self, search_results: List[Dict[str, str]]) -> FAISS:
        texts = [result["snippet"] for result in search_results]
        metadatas = [{"source": result["link"]} for result in search_results]
        documents = self.text_splitter.create_documents(texts, metadatas=metadatas)
        return FAISS.from_documents(documents, self.embeddings)

    @handle_openai_api_error
    async def _generate_summary(self, query: str, vector_db: FAISS, prompt_template: str) -> str:
        relevant_docs = vector_db.similarity_search(query, k=3)
        docs_page_content = " ".join([doc.page_content for doc in relevant_docs])

        prompt = PromptTemplate(template=prompt_template, input_variables=["query", "docs"])
        chain = LLMChain(llm=self.llm, prompt=prompt)
        summary = chain.run(query=query, docs=docs_page_content)
        return summary.strip()

    async def drug_info(self, drug_name: str, include_interactions: Optional[bool] = False) -> DrugInfo:
        cache_key = f"drug_info:{drug_name}:{include_interactions}"
        cached_response = await self.cache.get(cache_key)

        if cached_response:
            return DrugInfo(**cached_response)

        query = f"{drug_name} drug information"
        search_results = await self._perform_search(query)
        vector_db = await self._create_vector_db(search_results)

        prompt_template = """
        Provide a comprehensive summary of the drug {query}, including the following information:
        1. Description
        2. Dosage
        3. Side effects

        Base your summary on the following information:
        {docs}

        Format the summary as a JSON object with the keys: description, dosage, side_effects.
        """
        summary = await self._generate_summary(query, vector_db, prompt_template)

        try:
            response = json.loads(summary)
        except json.JSONDecodeError:
            response = {"error": "Failed to parse the summary"}

        response["name"] = drug_name

        if include_interactions:
            interactions_query = f"{drug_name} drug interactions"
            interactions_prompt = """
            Summarize the drug interactions for {query} based on the following information:
            {docs}

            Provide the summary as a simple string.
            """
            interactions_summary = await self._generate_summary(interactions_query, vector_db, interactions_prompt)
            response["interactions"] = interactions_summary
            await self.cache.set(cache_key, response)
            return DrugInfo(
                name=response["name"],
                description=response.get("description"),
                dosage=response.get("dosage"),
                side_effects=response.get("side_effects"),
                interactions=response.get("interactions"),
            )

        await self.cache.set(cache_key, response)
        return DrugInfo(
            name=response["name"],
            description=response.get("description"),
            dosage=response.get("dosage"),
            side_effects=response.get("side_effects"),
        )

    async def disease_info(self, disease_name: str, include_treatments: Optional[bool] = False) -> DiseaseInfo:
        cache_key = f"disease_info:{disease_name}:{include_treatments}"
        cached_response = await self.cache.get(cache_key)

        if cached_response:
            return DiseaseInfo(**cached_response)

        query = f"{disease_name} disease information"
        search_results = await self._perform_search(query)
        vector_db = await self._create_vector_db(search_results)

        prompt_template = """
        Provide a comprehensive summary of the disease {query}, including the following information:
        1. Description
        2. Symptoms
        3. Causes

        Base your summary on the following information:
        {docs}

        Format the summary as a JSON object with the keys: description, symptoms, causes.
        """
        summary = await self._generate_summary(query, vector_db, prompt_template)

        try:
            response = json.loads(summary)
        except json.JSONDecodeError:
            response = {"error": "Failed to parse the summary"}

        response["name"] = disease_name

        if include_treatments:
            treatments_query = f"{disease_name} disease treatments"
            treatments_prompt = """
            Summarize the treatments for {query} based on the following information:
            {docs}

            Provide the summary as a simple string.
            """
            treatments_summary = await self._generate_summary(treatments_query, vector_db, treatments_prompt)
            response["treatments"] = treatments_summary

        await self.cache.set(cache_key, response)  # Cache the response
        return DiseaseInfo(
            name=response["name"],
            description=response.get("description"),
            symptoms=response.get("symptoms"),
            causes=response.get("causes"),
            treatments=response.get("treatments") if include_treatments else None,
        )

    async def close(self) -> None:
        """Close the Redis connection."""
        await self.cache.close()

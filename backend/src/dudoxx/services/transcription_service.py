import os
import tempfile
from fastapi import UploadFile, HTTPException
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from openai import OpenAI
from dudoxx.exceptions.openai_exceptions import handle_openai_api_error
from dudoxx.services.redis_service import RedisCacheService


class TranscriptionService:
    def __init__(self):
        self.openai_client = OpenAI()
        self.chat_model = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
        self.cache_service = RedisCacheService()

    async def process_audio(self, audio_file: UploadFile, target_language: str, task_id: str):
        try:
            transcription = await self.transcribe_audio(audio_file, target_language)
            translation = None
            if target_language != "en":
                translation = await self.translate_text(transcription, target_language)

            task_data = {
                "status": "completed",
                "transcription": transcription,
                "translation": translation,
                "progress": 100,
            }
            await self.cache_service.set(task_id, task_data)
        except Exception as e:
            await self.cache_service.set(task_id, {"status": "failed", "error": str(e)})

    @handle_openai_api_error
    async def transcribe_audio(self, audio_file: UploadFile, target_language: str) -> str:
        if audio_file.content_type not in ["audio/mpeg", "audio/wav", "audio/x-m4a"]:
            raise HTTPException(status_code=400, detail="Unsupported audio format")

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=self._get_file_extension(audio_file.filename)
        ) as temp_file:
            temp_file.write(await audio_file.read())
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as audio:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio, response_format="text"
                )
            return transcript
        finally:
            os.unlink(temp_file_path)

    @handle_openai_api_error
    async def translate_text(self, text: str, target_language: str) -> str:
        prompt = PromptTemplate(
            input_variables=["text", "language"], template="Translate the following text to {language}: {text}"
        )
        chain = LLMChain(llm=self.chat_model, prompt=prompt)
        result = await chain.arun(text=text, language=target_language)
        return result.strip()

    @staticmethod
    def _get_file_extension(filename: str) -> str:
        return os.path.splitext(filename)[1].lower()

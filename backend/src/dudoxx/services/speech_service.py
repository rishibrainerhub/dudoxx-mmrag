# speech_service.py
import os
import tempfile
import asyncio
from typing import Optional, Tuple
from fastapi import HTTPException
from openai import OpenAI
from dudoxx.exceptions.openai_exceptions import handle_openai_api_error
from dudoxx.services.redis_service import RedisCacheService


class SpeechService:
    def __init__(self):
        self.openai_client = OpenAI()
        self.cache_service = RedisCacheService()
        self.SUPPORTED_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.DEFAULT_VOICE = "nova"

    async def process_speech_generation(self, text: str, task_id: str, voice: Optional[str] = None):
        """Process speech generation in background task"""
        try:
            # Update initial status
            await self.cache_service.set(task_id, {"status": "processing", "progress": 0})

            # Run the synchronous OpenAI call in a thread pool
            speech_data = await self._generate_speech_sync(text, voice)

            # Create temporary file path
            temp_file_path = os.path.join(tempfile.gettempdir(), f"{task_id}.mp3")

            # Write file in a non-blocking way
            await self._write_file_async(temp_file_path, speech_data)

            # Update cache with success status and file location
            await self.cache_service.set(
                task_id,
                {"status": "completed", "file_path": temp_file_path, "content_type": "audio/mpeg", "progress": 100},
            )

        except Exception as e:
            # Update cache with error status
            error_message = f"Speech generation failed: {str(e)}"
            await self.cache_service.set(task_id, {"status": "failed", "error": error_message, "progress": 0})

    async def _generate_speech_sync(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate speech using OpenAI's API in a non-blocking way"""
        if not text:
            raise ValueError("Text cannot be empty")

        if len(text) > 4096:
            raise ValueError("Text length exceeds maximum limit of 4096 characters")

        voice = voice if voice in self.SUPPORTED_VOICES else self.DEFAULT_VOICE

        try:
            # Run the synchronous OpenAI call in a thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._call_openai_api, text, voice)
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _call_openai_api(self, text: str, voice: str) -> bytes:
        """Synchronous OpenAI API call"""
        try:
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )
            return response.content
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")

    @staticmethod
    async def _write_file_async(file_path: str, content: bytes):
        """Write file in a non-blocking way"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: open(file_path, "wb").write(content))

    async def get_speech_file(self, task_id: str) -> Tuple[str, str]:
        """Retrieve generated speech file details"""
        task_data = await self.cache_service.get(task_id)

        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")

        if task_data["status"] == "failed":
            raise HTTPException(status_code=500, detail=task_data.get("error", "Unknown error"))

        if task_data["status"] == "processing":
            raise HTTPException(status_code=202, detail="Processing")

        return task_data["file_path"], task_data["content_type"]

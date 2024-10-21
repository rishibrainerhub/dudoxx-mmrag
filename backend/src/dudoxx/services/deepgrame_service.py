# transcription_service.py
import os
import tempfile
import aiofiles
from typing import Optional
from fastapi import HTTPException, UploadFile
import uuid
from deepgram import DeepgramClient, PrerecordedOptions, DeepgramClientOptions

from dudoxx.exceptions.deepgram_exceptions import handle_deepgram_api_error
from dudoxx.services.redis_service import RedisCacheService


class DeepgramService:
    def __init__(self) -> None:
        self.base_url = "https://deepgram-telekom.dudoxx.com"
        self.config = DeepgramClientOptions(
            url=self.base_url,
            options={
                "keepalive": False,
            },
        )
        self.deepgram_client = DeepgramClient(api_key="No key", config=self.config)
        self.cache_service = RedisCacheService()

    async def process_transcription(self, file: UploadFile, task_id: str, language: Optional[str] = None) -> None:
        """Process audio transcription in background task"""
        try:
            # Update initial status
            await self.cache_service.set(task_id, {"status": "processing", "progress": 0})

            # Save uploaded file temporarily
            temp_file_path = os.path.join(tempfile.gettempdir(), f"{task_id}_{file.filename}")
            await self._save_file_async(temp_file_path, file)

            # Run the transcription
            transcription_result = await self._transcribe_audio(temp_file_path, language)

            # Update cache with success status and transcription result
            await self.cache_service.set(
                task_id,
                {
                    "status": "completed",
                    "transcription": transcription_result["text"],
                    "confidence": transcription_result["confidence"],
                    "progress": 100,
                },
            )

            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        except Exception as e:
            # Update cache with error status
            error_message = f"Transcription failed: {str(e)}"
            await self.cache_service.set(task_id, {"status": "failed", "error": error_message, "progress": 0})
            # Re-raise the exception for proper error handling
            raise

    @handle_deepgram_api_error
    async def _transcribe_audio(self, file_path: str, language: Optional[str] = None) -> dict:
        """Transcribe audio using Deepgram's API"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            async with aiofiles.open(file_path, "rb") as audio:
                buffer_data = await audio.read()

                # Configure transcription options
                options = PrerecordedOptions(
                    model="nova-2",
                    smart_format=True,
                    language=language if language else "en",
                )

                # Send transcription request
                response = self.deepgram_client.listen.rest.v("1").transcribe_file({"buffer": buffer_data}, options)
                # Extract results
                if response and response.results:
                    channels = response.results.channels
                    if channels and channels[0].alternatives:
                        return {
                            "text": channels[0].alternatives[0].transcript,
                            "confidence": channels[0].alternatives[0].confidence,
                        }

                raise ValueError("No transcription alternatives found in the response")
        except Exception as e:
            raise Exception(f"Deepgram API error: {str(e)}")

    @staticmethod
    async def _save_file_async(file_path: str, file: UploadFile) -> None:
        """Save uploaded file in a non-blocking way"""
        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)
        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")

    async def get_transcription_result(self, task_id: str) -> dict:
        """Retrieve transcription result"""
        task_data = await self.cache_service.get(task_id)

        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")

        if task_data["status"] == "failed":
            raise HTTPException(status_code=500, detail=task_data.get("error", "Unknown error"))

        if task_data["status"] == "processing":
            raise HTTPException(status_code=202, detail="Processing")

        return {"transcription": task_data["transcription"], "confidence": task_data["confidence"]}

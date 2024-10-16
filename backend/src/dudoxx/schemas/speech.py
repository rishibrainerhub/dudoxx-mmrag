from typing import Optional
from pydantic import BaseModel, Field


class SpeechRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    voice: Optional[str] = Field(None, description="Voice ID for speech generation")


class SpeechTaskResponse(BaseModel):
    task_id: str
    status: str
    progress: int = 0

from typing import Optional
from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    transcription: str
    translation: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    status: str

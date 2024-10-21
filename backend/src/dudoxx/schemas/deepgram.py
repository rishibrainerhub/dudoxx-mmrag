import uuid
from pydantic import BaseModel


class AudioTaskResponse(BaseModel):
    task_id: uuid.UUID
    status: str


class AudioTranscriptionResponse(BaseModel):
    transcription: str
    confidence: float

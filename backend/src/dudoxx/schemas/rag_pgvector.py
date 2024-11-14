from pydantic import BaseModel
from typing import List
import uuid


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence_score: float


class DocumentTaskResponse(BaseModel):
    task_id: str
    status: str
    progress: int = 0

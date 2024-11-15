from pydantic import BaseModel
from typing import List, Optional


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence_score: float
    context_id: Optional[str] = None


class DocumentTaskResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    context_id: Optional[str] = None

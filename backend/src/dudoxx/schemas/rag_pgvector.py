from pydantic import BaseModel
from typing import List


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence_score: float


class DocumentResponse(BaseModel):
    id: int
    status: str
    message: str

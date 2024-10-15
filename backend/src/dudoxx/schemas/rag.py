from pydantic import BaseModel, Field
from typing import List


class Query(BaseModel):
    text: str


class Answer(BaseModel):
    content: str


class StructuredAnswer(BaseModel):
    answer: str = Field(description="The main answer to the query")
    sources: List[str] = Field(description="List of sources used to generate the answer")
    confidence: float = Field(description="Confidence score of the answer", ge=0, le=1)


class EnhancedAnswer(BaseModel):
    content: str
    sources: List[str]
    confidence: float

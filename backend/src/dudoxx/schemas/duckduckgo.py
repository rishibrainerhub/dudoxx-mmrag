from typing import Optional
from pydantic import BaseModel


class DrugInfo(BaseModel):
    name: str
    description: str
    dosage: str
    side_effects: str


class DiseaseInfo(BaseModel):
    name: str
    description: str
    symptoms: str
    causes: str
    treatments: Optional[str] = None

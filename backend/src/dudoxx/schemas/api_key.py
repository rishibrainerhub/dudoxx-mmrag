from pydantic import BaseModel


class ApiKeyResponse(BaseModel):
    key: str

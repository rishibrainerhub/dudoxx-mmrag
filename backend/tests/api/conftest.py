import pytest
from fastapi.testclient import TestClient

from sqlalchemy.orm import Session
from contextlib import suppress

from dudoxx.app import create_app
from dudoxx.database.sqlite.database import get_db
from dudoxx.services.api_key_management_service import APIKeyManagerService
from dudoxx.exceptions.apikey_exceptions import APIKeyCreationError


@pytest.fixture
def client():
    app = create_app(is_test=True)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def database() -> Session:
    return next(get_db())


class ApiKeyApiTestDriver:
    def __init__(self, database: Session):
        self.database = database
        self.service = APIKeyManagerService(database)
        self.created_keys = []

    async def __aenter__(self) -> "ApiKeyApiTestDriver":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.revoke_api_keys()

    async def create_new_api_key(self):
        key = await self.service.create_new_api_key()
        self.created_keys.append(key)
        return key

    async def revoke_api_keys(self):
        for key in self.created_keys:
            with suppress(APIKeyCreationError):
                await self.service.revoke_api_key(key.key)

import pytest
import os
import hashlib
from sqlalchemy.orm import Session
from contextlib import suppress

from dudoxx.database.sqlite.database import get_db
from dudoxx.services.api_key_management_service import APIKeyManagerService
from dudoxx.exceptions.apikey_exceptions import APIKeyCreationError


@pytest.fixture
def database() -> Session:
    return next(get_db())


def current_test() -> str:
    return os.environ["PYTEST_CURRENT_TEST"]


def current_test_hash() -> str:
    return hashlib.sha1(current_test().encode("utf8")).hexdigest()


class ApiKeyServiceDriver:
    def __init__(self, database: Session):
        self.database = database
        self.service = APIKeyManagerService(database)
        self.created_keys = []

    async def __aenter__(self) -> "ApiKeyServiceDriver":
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

import pytest

from dudoxx.services.api_key_management_service import APIKeyManagerService
from dudoxx.schemas.api_key import ApiKeyResponse
from dudoxx.exceptions.apikey_exceptions import ApiKeyNotFound
from conftest import ApiKeyServiceDriver


class TestApiKeyGenerationService:
    @pytest.mark.asyncio
    async def test_should_generate_api_key(self, database):
        service = APIKeyManagerService(database)
        key = None
        try:
            api_key = await service.create_new_api_key()
            key = api_key.key
            assert isinstance(api_key, ApiKeyResponse)
            api_key.key = key[:8]
            api_keys = await service.list_api_keys()
            assert api_key in api_keys
        finally:
            if key:
                await service.revoke_api_key(key)


class TestApiKeyValidationService:
    @pytest.mark.asyncio
    async def test_should_validate_api_key(self, database):
        service = APIKeyManagerService(database)

        async with ApiKeyServiceDriver(database) as driver:
            key = await driver.create_new_api_key()
            assert await service.validate_api_key(key.key, database)

    @pytest.mark.asyncio
    async def test_should_not_validate_invalid_api_key(self, database):
        service = APIKeyManagerService(database)
        assert not await service.validate_api_key("invalid_key", database)


class TestListApiKeys:
    @pytest.mark.asyncio
    async def test_should_list_api_keys(self, database):
        service = APIKeyManagerService(database)
        async with ApiKeyServiceDriver(database) as driver:
            api_key = await driver.create_new_api_key()
            key = api_key.key
            api_key.key = key[:8]
            api_keys = await service.list_api_keys()
            assert api_key in api_keys


class TestRevokeApiKey:
    @pytest.mark.asyncio
    async def test_should_revoke_api_key(self, database):
        service = APIKeyManagerService(database)

        # Create a new API key
        api_key = await service.create_new_api_key()
        key = api_key.key
        api_key.key = key[:8]

        # Revoke the API key
        await service.revoke_api_key(key)

        # Validate that the API key is revoked
        api_keys = await service.list_api_keys()
        assert api_key not in api_keys

    @pytest.mark.asyncio
    async def test_should_not_revoke_invalid_api_key(self, database):
        service = APIKeyManagerService(database)
        with pytest.raises(ApiKeyNotFound):
            await service.revoke_api_key("invalid_key")

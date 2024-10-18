import pytest
from dudoxx.services.api_key_management_service import APIKeyManagerService


class TestCreateApikeyApi:
    @pytest.mark.asyncio
    async def test_should_create_api_key(self, client, database):
        key = None
        try:
            response = client.post("/api/v1/create_api_key")
            assert response.status_code == 200
            data = response.json()
            key = data["key"][:8]

            service = APIKeyManagerService(database)
            api_keys = await service.list_api_keys()
            assert key in [api_key.key for api_key in api_keys]

        finally:
            if key:
                service = APIKeyManagerService(database)
                await service.revoke_api_key(key)

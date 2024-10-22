import pytest
from .conftest import ApiKeyApiTestDriver


class TestGetDrugInfoApi:
    @pytest.mark.asyncio
    async def test_should_not_return_drug_info_without_drug_name(self, client, database):
        async with ApiKeyApiTestDriver(database) as api_test_driver:
            apikey = await api_test_driver.create_new_api_key()

            response = client.get("/api/v1/drug_info/", headers={"x-api-key": apikey.key})
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_drug_info_without_interactions(self, client, database):
        async with ApiKeyApiTestDriver(database) as api_test_driver:
            apikey = await api_test_driver.create_new_api_key()
            response = client.get("/api/v1/drug_info/paracetamol", headers={"x-api-key": apikey.key})
            assert response.status_code == 200
            drug_info = response.json()
            assert drug_info["name"] == "paracetamol"
            assert drug_info["description"] != ""
            assert drug_info["dosage"] != ""
            assert drug_info["side_effects"] != ""
            assert drug_info["interactions"] is None

    @pytest.mark.asyncio
    async def test_should_return_drug_info_with_interactions(self, client, database):
        async with ApiKeyApiTestDriver(database) as api_test_driver:
            apikey = await api_test_driver.create_new_api_key()
            response = client.get(
                "/api/v1/drug_info/paracetamol?include_interactions=true", headers={"x-api-key": apikey.key}
            )
            assert response.status_code == 200
            drug_info = response.json()
            assert drug_info["name"] == "paracetamol"
            assert drug_info["description"] != ""
            assert drug_info["dosage"] != ""
            assert drug_info["side_effects"] != ""
            assert drug_info["interactions"] != ""

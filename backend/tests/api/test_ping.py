import pytest


class TestPingApi:
    def test_ping(self, client):
        response = client.get("/ping")
        assert response.status_code == 200

import pytest
from fastapi.testclient import TestClient
from dudoxx.app import app


@pytest.fixture
def client():
    return TestClient(app)

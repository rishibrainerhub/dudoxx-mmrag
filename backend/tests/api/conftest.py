import pytest
from fastapi.testclient import TestClient
from dudoxx.app import create_app
from dudoxx.database.sqlite.database import get_db
from sqlalchemy.orm import Session


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture
def database() -> Session:
    return next(get_db())

import pytest
from fastapi.testclient import TestClient

from madr_api.app import app


@pytest.fixture
def client():
    return TestClient(app)

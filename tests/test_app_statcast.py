from fastapi.testclient import TestClient

from app_statcast import __version__
from app_statcast.main import app

client = TestClient(app)


def test_version():
    assert __version__ == "0.1.0"


def test_read_pitch():
    response = client.get("/pitches/191031_034516")
    assert response.status_code == 200

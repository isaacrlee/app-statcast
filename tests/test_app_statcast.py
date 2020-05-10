from app_statcast import __version__
from app_statcast.main import app
from fastapi.testclient import TestClient
import pandas as pd


client = TestClient(app)


def test_version():
    assert __version__ == "0.1.0"


def test_read_pitch():
    response = client.get("/pitchbypitch/191031_034516")

    df = pd.read_json(response.json())

    assert len(df.index) > 0
    assert "swing" in df.columns and "miss" in df.columns
    assert response.status_code == 200


def test_read_pitches():
    response = client.get("/pitchbypitch/?batter=545361&pitcher=543037")

    df = pd.read_json(response.json())

    assert len(df.index) > 0
    assert "swing" in df.columns and "miss" in df.columns
    assert response.status_code == 200


def test_read_pitches_400():
    response = client.get("/pitchbypitch/")

    assert response.status_code == 400

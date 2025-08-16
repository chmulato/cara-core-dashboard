from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_data_returns_snapshot():
    r = client.get("/api/data")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "linhas" in data


def test_api_historico_limit():
    r = client.get("/api/historico?limit=2")
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) <= 2

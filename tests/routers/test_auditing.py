import pytest
from starlette.testclient import TestClient


@pytest.mark.apitest
def test_auditing_manual(capfd, client: TestClient):
    response = client.get("/auditing/manual")
    data = response.json()
    assert response.status_code == 200
    assert data["hello"] == "world"

    stdout, stderr = capfd.readouterr()

    assert len(stdout.split("\n")) == 5


@pytest.mark.apitest
def test_auditing_automatic(capfd, client: TestClient):
    response = client.get("/auditing/automatic")
    data = response.json()
    assert response.status_code == 200
    assert data["hello"] == "world"

    stdout, stderr = capfd.readouterr()

    assert len(stdout.split("\n")) == 3

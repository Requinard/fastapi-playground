"""
Test HTTP Auth Header Passthrough. Also include RESPX for HTTP mocking.
"""
import httpx
import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize("auth_token", [None, "auth header"])
def test_async_passthrough(auth_token, client: TestClient):
    response = client.get("/auth-passthrough/async", headers={
        "Authorization": auth_token
    })

    assert response.status_code == 200

    data = response.json()

    assert data['auth_token'] == auth_token

@pytest.mark.parametrize("auth_token", [None, "auth header"])
def test_sync_passthrough(auth_token, client: TestClient):
    response = client.get("/auth-passthrough/sync", headers={
        "Authorization": auth_token
    })

    assert response.status_code == 200

    data = response.json()

    assert data['auth_token'] == auth_token

@pytest.mark.respx(base_url="https://ifconfig.me")
def test_respx_mock(client: TestClient, respx_mock):
    respx_mock.get("/ip").mock(return_value=httpx.Response(204, content="127.0.0.1"))
    response = client.get("/auth-passthrough/sync")

    assert response.status_code == 200

    data = response.json()

    assert data['auth_token'] == None
    assert data['ip'] == "127.0.0.1"


@pytest.mark.respx(base_url="https://ifconfig.me")
def test_respx_mock_with_failure(client: TestClient, respx_mock):
    respx_mock.get("/ip").mock(return_value=httpx.Response(404, content="haha suck it"))

    response = client.get("/auth-passthrough/sync")

    assert response.status_code == 400

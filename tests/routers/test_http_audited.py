import pytest
from starlette.testclient import TestClient


@pytest.mark.apitest
def test_http_audit_success(capfd, client: TestClient, snapshot):
    response = client.get("/http-audited/success")

    assert response.status_code == 200

    stdout, stderr = capfd.readouterr()

    assert len(stdout.split("\n")) == 4
    snapshot.assert_match(stdout, "http_audit_success")


@pytest.mark.apitest
def test_http_audit_fail(capfd, client: TestClient, snapshot):
    response = client.get("/http-audited/fail")

    assert response.status_code == 422

    stdout, stderr = capfd.readouterr()
    assert len(stdout.split("\n")) == 4
    snapshot.assert_match(stdout, "http_audit_fail")

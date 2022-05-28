import pytest
import schemathesis
from starlette.testclient import TestClient


@pytest.fixture
def web_app(client: TestClient):
    return schemathesis.from_dict(client.app.openapi())


schema = schemathesis.from_pytest_fixture("web_app")


@schema.parametrize()
def test_api(case, client: TestClient):
    case.call_and_validate(session=client)

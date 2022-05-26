from starlette.testclient import TestClient

from playground.paginator import PAGINATED_SIZE, PaginatedResult


def test_unpaginated(client: TestClient):
    response = client.get("/pagination/unpaginated")

    data = response.json()

    assert response.status_code == 200
    assert len(data) == PAGINATED_SIZE


def test_paginated_without_changes(client: TestClient):
    response = client.get("/pagination/paginated")

    data = PaginatedResult.parse_obj(response.json())

    assert response.status_code == 200
    assert len(data.data) == 100
    assert data.page_size == 100


def test_paginated_with_custom_page_size(client: TestClient):
    page_size = 5

    response = client.get("/pagination/paginated", params={'page_size': page_size})

    data = PaginatedResult.parse_obj(response.json())

    assert response.status_code == 200
    assert len(data.data) == page_size
    assert data.page_size == page_size


def test_paginated_with_a_page(client: TestClient):
    response = client.get("/pagination/paginated", params={'page': 5})

    data = PaginatedResult.parse_obj(response.json())

    assert response.status_code == 200
    assert len(data.data) == 100
    assert data.page_size == 100
    assert data.page == 5


def test_paginated_with_a_page_beyond_bounds(client: TestClient):
    response = client.get("/pagination/paginated", params={'page': 10000})

    data = PaginatedResult.parse_obj(response.json())

    assert response.status_code == 200
    assert len(data.data) == 0
    assert data.page_size == 100
    assert data.page == 10000


def test_paginated_with_negative_page(client: TestClient):
    response = client.get("/pagination/paginated", params={'page': -5})

    assert response.status_code == 422


def test_paginated_with_negative_page_size(client: TestClient):
    response = client.get("/pagination/paginated", params={'page_size': -5})

    assert response.status_code == 422


def test_paginated_with_largest_page_size(client: TestClient):
    response = client.get("/pagination/paginated", params={'page_size': 10e6})

    assert response.status_code == 422

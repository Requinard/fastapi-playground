from datetime import datetime

import pytest
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.testclient import TestClient

from playground.routers.time_range import TimeRangedModel


@pytest.fixture(autouse=True)
async def create_comments(async_session: AsyncSession):
    comment = TimeRangedModel(
        comment="Hey uhh guys, watch out for this Covid19 thing ok?",
        date_created=datetime(year=2020, month=3, day=11)
    )

    async_session.add(comment)
    await async_session.commit()


@pytest.mark.apitest
def test_get_comments_works(client: TestClient):
    response = client.get("/timeranged/")

    data = response.json()

    assert len(data) == 1


@pytest.mark.apitest
def test_comments_exclude_with_time_from(client: TestClient):
    response = client.get("/timeranged/", params={
        'time_from': datetime.now()
    })

    data = response.json()

    assert len(data) == 0


@pytest.mark.apitest
def test_comments_include_with_time_from(client: TestClient):
    response = client.get("/timeranged/", params={
        'time_from': datetime(year=2020, month=1, day=1)
    })

    data = response.json()

    assert len(data) == 1


@pytest.mark.apitest
def test_exclude_with_time_to(client: TestClient):
    response = client.get("/timeranged/", params={
        'time_to': datetime(year=2020, month=1, day=1)
    })

    data = response.json()

    assert len(data) == 0


@pytest.mark.apitest
def test_include_with_time_to(client: TestClient):
    response = client.get("/timeranged/", params={
        'time_to': datetime(year=2022, month=1, day=1)
    })

    data = response.json()

    assert len(data) == 1


@pytest.mark.apitest
def test_with_paginator_first_page(client: TestClient):
    response = client.get("/timeranged")

    data = response.json()

    assert len(data) == 1


@pytest.mark.apitest
def test_paginator_with_empty_page(client: TestClient):
    response = client.get("/timeranged", params={
        'page': 500
    })

    data = response.json()

    assert len(data) == 0

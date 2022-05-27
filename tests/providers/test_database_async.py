import pytest

from playground.providers.database_async import get_session, get_engine


@pytest.mark.anyio
async def test_async_engine_same():
    e1 = await get_engine()
    e2 = await get_engine()

    assert e1 is e2

@pytest.mark.anyio
async def test_async_session_not_same():
    s1 = get_session()
    s2 = get_session()

    assert s1 is not s2


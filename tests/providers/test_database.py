from playground.providers.database import get_database_engine, get_session


def test_engine_is_cached():
    e1 = get_database_engine()
    e2 = get_database_engine()

    assert e1 is e2


def test_session_is_different():
    s1 = get_session()
    s2 = get_session()

    assert s1 is not s2

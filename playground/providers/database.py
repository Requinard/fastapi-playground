from functools import lru_cache
from sqlalchemy.engine import Engine
from sqlmodel import create_engine, SQLModel, Session

from playground.providers.settings import get_settings


@lru_cache(None)
def get_database_engine(settings = get_settings()) -> Engine:
    """
    Create an engine and memoize the results. This ensures we only create a single engine.
    """
    sqlite_url = f"sqlite:///{settings.database_url}"

    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, echo=settings.database_echo, echo_pool=settings.database_echo, connect_args=connect_args)

    SQLModel.metadata.create_all(engine)

    return engine


def get_session():
    """
    Yield a session that can be used as a FastAPI dependency
    """
    engine = get_database_engine()
    with Session(engine) as session:
        yield session

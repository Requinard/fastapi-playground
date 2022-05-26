from pydantic.tools import lru_cache
from sqlalchemy.engine import Engine
from sqlmodel import create_engine, SQLModel, Session


@lru_cache
def get_database_engine() -> Engine:
    """
    Create an engine and memoize the results. This ensures we only create a single engine.
    """
    sqlite_file_name = "../../database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

    SQLModel.metadata.create_all(engine)

    return engine


def get_session():
    """
    Yield a session that can be used as a FastAPI dependency
    """
    engine = get_database_engine()
    with Session(engine) as session:
        yield session

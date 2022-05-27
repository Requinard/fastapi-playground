import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from playground.main import app
from playground.providers.database import get_session as get_sync_session
from playground.providers.database_async import get_session as get_async_session

pytestmark = pytest.mark.anyio

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="async_session")
async def async_session_fixture():
    engine = create_async_engine(f"sqlite+aiosqlite://", poolclass=StaticPool, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session, async_session: AsyncSession):
    def get_session_override():
        return session

    app.dependency_overrides[get_sync_session] = get_session_override
    app.dependency_overrides[get_async_session] = lambda: async_session

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def anyio_backend():
    return 'asyncio'

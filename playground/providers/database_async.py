from async_lru import alru_cache
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from playground.providers.settings import get_settings


@alru_cache(maxsize=1)
async def get_engine() -> AsyncEngine:
    settings = get_settings()
    engine = create_async_engine(f"sqlite+aiosqlite:///{settings.database_url}", echo=settings.database_echo, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    return engine


async def get_session() -> AsyncSession:
    engine = await get_engine()
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

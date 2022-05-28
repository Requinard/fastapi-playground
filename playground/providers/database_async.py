from async_lru import alru_cache
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from playground.providers.settings import get_settings


@alru_cache(maxsize=1)
async def get_engine() -> AsyncEngine:
    """
    Create the database engine and initialize all models.

    @alru_cache ensures that there can only every be a single async engine.
    :return:
    """
    settings = get_settings()
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{settings.database_url}",
        echo=settings.database_echo,
        future=True,
    )

    async with engine.begin() as conn:
        # Do not do this with actual databases. This runs the DDL
        await conn.run_sync(SQLModel.metadata.create_all)

    return engine


async def get_session() -> AsyncSession:
    """
    Create a temporary session that we can use to query the database.
    """
    engine = await get_engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

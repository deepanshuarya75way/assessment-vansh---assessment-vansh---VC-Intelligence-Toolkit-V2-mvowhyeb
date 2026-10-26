from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.pool import NullPool

from app.core.config import settings

async_engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def _get_async_database_url() -> str:
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return database_url


def get_async_engine() -> AsyncEngine:
    global async_engine

    if async_engine is None:
        if not settings.database_url:
            raise RuntimeError(
                "DATABASE_URL must be configured before using database sessions."
            )
        database_url = _get_async_database_url()
        async_engine = create_async_engine(
            database_url,
            connect_args={"statement_cache_size": 0},
            pool_pre_ping=True,
            poolclass=NullPool,
        )

    return async_engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global AsyncSessionLocal

    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )

    return AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_sessionmaker()() as session:
        yield session

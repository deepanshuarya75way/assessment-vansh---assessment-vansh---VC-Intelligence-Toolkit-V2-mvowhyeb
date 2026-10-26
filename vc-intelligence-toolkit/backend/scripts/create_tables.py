import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.database.base import Base
from app.database.session import get_async_engine

# Import models so they are registered on Base.metadata.
import app.models  # noqa: F401


async def create_tables() -> None:
    if not settings.database_url:
        print("DATABASE_URL is not set; skipping table creation.")
        return

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())

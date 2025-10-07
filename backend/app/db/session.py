from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from app.core.settings import settings
import os

# Ensure the directory exists for SQLite (if using fallback)
if settings.DATABASE_URL.startswith(("sqlite", "sqlite+aiosqlite")):
    os.makedirs("var", exist_ok=True)

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncIterator[AsyncSession]:
    """
    Dependency provider for an async database session.

    Yields:
        AsyncSession: An active database session.
    """
    async with SessionLocal() as session:
        yield session
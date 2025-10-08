import os
import tempfile
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.settings import settings
from app.db.uow import UnitOfWork
from app.db.base import Base as models_base  # suppose que Base est exporté ici

@pytest.fixture(scope="session")
def sqlite_url() -> tuple[str, tempfile.TemporaryDirectory]:
    """
    Provides a temporary SQLite database URL for testing.

    Returns:
        tuple: The database URL for a temporary SQLite file and the TemporaryDirectory object.
    """
    tmpdir = tempfile.TemporaryDirectory()
    path = os.path.join(tmpdir.name, "test.db")
    url = f"sqlite+aiosqlite:///{path}"
    return url, tmpdir

@pytest.fixture(scope="session")
async def engine(sqlite_url):
    """
    Creates an async SQLAlchemy engine and initializes all tables for the test session.

    Args:
        sqlite_url (tuple): The database URL and TemporaryDirectory.

    Yields:
        AsyncEngine: The SQLAlchemy async engine.
    """
    url, tmpdir = sqlite_url
    engine = create_async_engine(url, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(models_base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()
        tmpdir.cleanup()

@pytest.fixture(scope="function")
def session_maker(engine):
    """
    Provides a session maker for async SQLAlchemy sessions, scoped to each test function.

    Args:
        engine (AsyncEngine): The SQLAlchemy async engine.

    Returns:
        async_sessionmaker: Factory for async sessions.
    """
    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture
async def db_session(session_maker) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an async SQLAlchemy session for each test, with transaction rollback for isolation.

    Args:
        session_maker (async_sessionmaker): Factory for async sessions.

    Yields:
        AsyncSession: The database session for the test.
    """
    async with session_maker() as session:
        trans = await session.begin()
        try:
            yield session
        finally:
            try:
                await trans.rollback()
            except Exception:
                pass  # Ignore ResourceClosedError

@pytest.fixture(autouse=True)
def _test_settings(sqlite_url, monkeypatch):
    """
    Automatically sets environment variables and settings for tests.
    Forces the app into DEV mode, sets a test secret, and uses the test database.

    Args:
        sqlite_url (tuple): The test database URL and TemporaryDirectory.
        monkeypatch: Pytest fixture for patching environment variables.
    """
    url, _ = sqlite_url
    monkeypatch.setenv("ENV", "dev")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    monkeypatch.setenv("DATABASE_URL", url)

    # Dynamically reload settings if the object is frozen at startup
    settings.ENV = "dev"
    settings.SECRET_KEY = "test-secret"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
    settings.DATABASE_URL = url

@pytest.fixture(autouse=True)
def override_uow(db_session):
    """
    Overrides the get_uow dependency to inject the test session into the UnitOfWork.

    Args:
        db_session (AsyncSession): The test database session.
    """
    from app.db.uow import get_uow

    async def _get_uow_override():
        yield UnitOfWork(session=db_session)

    app.dependency_overrides[get_uow] = _get_uow_override
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_token(client) -> str:
    """
    Helper fixture to log in as a test user and retrieve a JWT access token.

    Args:
        client (AsyncClient): The HTTPX async client.

    Returns:
        str: The JWT access token for the test user.
    """
    r = await client.post("/auth/login", params={"display": "Tester"})
    assert r.status_code == 200
    return r.json()["access_token"]
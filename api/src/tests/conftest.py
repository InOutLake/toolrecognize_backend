import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.settings import SETTINGS
from infrastructure.database.database import get_db
from main import app


@pytest_asyncio.fixture(scope="function")
async def engine():
    engine = create_async_engine(SETTINGS.database_url, pool_size=5, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(engine):
    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with session_factory() as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def patched_app(test_db_session):
    async def override_dependency():
        yield test_db_session

    app.dependency_overrides[get_db] = override_dependency
    yield app
    app.dependency_overrides.pop(get_db)


@pytest_asyncio.fixture(scope="function")
async def async_client(patched_app):
    async with AsyncClient(
        transport=ASGITransport(app=patched_app), base_url="http://testserver"
    ) as ac:
        yield ac
    await ac.aclose()

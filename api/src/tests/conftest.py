from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from main import app
from infrastructure.database.database import AsyncSessionLocal, get_db


# fixes sharing database connection between tests
@pytest_asyncio.fixture(scope="function")
async def test_async_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_db(test_async_session):
    app.dependency_overrides[get_db] = lambda: test_async_session
    yield
    app.dependency_overrides.pop(get_db)


@pytest_asyncio.fixture(scope="function")
async def async_client(override_db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac

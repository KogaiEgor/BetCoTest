import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.bets.db import Base, AsyncSessionLocal


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/bet_maker_test"


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
async def async_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

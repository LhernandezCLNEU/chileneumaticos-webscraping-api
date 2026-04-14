import asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app import main as app_module
from app.models.base import Base
from app.db import get_db

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(prepare_database):
    # override dependency
    app_module.app.dependency_overrides[get_db] = lambda: override_get_db()
    from httpx import AsyncClient

    async with AsyncClient(app=app_module.app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session(prepare_database):
    async with TestingSessionLocal() as session:
        yield session

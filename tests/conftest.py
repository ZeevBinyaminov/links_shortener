import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import delete


from src.core.db import get_db
from src.core.config import DB_HOST_TEST, DB_PORT_TEST, DB_NAME_TEST, DB_USER_TEST, DB_PASS_TEST
from src.main import app
from src.core.db import Base
from src.auth.models import User
from src.links.models import Stats, Url


DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, expire_on_commit=False, class_=AsyncSession)
Base.metadata.bind = engine_test


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


async def _create_test_db() -> None:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _drop_test_db() -> None:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _cleanup_db() -> None:
    async with async_session_maker() as session:
        await session.execute(delete(Stats))
        await session.execute(delete(Url))
        await session.execute(delete(User))
        await session.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    asyncio.run(_create_test_db())
    yield
    asyncio.run(_drop_test_db())


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

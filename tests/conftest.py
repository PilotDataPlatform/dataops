# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

import asyncio
import os

import httpx
import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from faker import Faker
from fakeredis.aioredis import FakeRedis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateTable
from testcontainers.postgres import PostgresContainer

from models.api_archive_sql import ArchivePreviewModel
from models.api_archive_sql import Base as ArchiveBase

RDS_SCHEMA_DEFAULT = os.environ['RDS_SCHEMA_DEFAULT']


@pytest.fixture(scope='session')
def db_postgres():
    with PostgresContainer('postgres:9.5') as postgres:
        yield postgres.get_connection_url().replace('+psycopg2', '+asyncpg')


@pytest_asyncio.fixture
async def engine(db_postgres):
    engine = create_async_engine(db_postgres)
    yield engine
    await engine.dispose()


class AsyncClient(httpx.AsyncClient):
    async def delete(self, url: str, **kwds) -> httpx.Response:
        """Default delete request doesn't support body."""

        return await self.request('DELETE', url, **kwds)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    asyncio.set_event_loop_policy(None)


@pytest_asyncio.fixture
async def test_client():
    from app import create_app

    app = create_app()
    async with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def create_db_archive(engine):
    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {RDS_SCHEMA_DEFAULT};'))
        await conn.execute(CreateTable(ArchivePreviewModel.__table__))
        await conn.run_sync(ArchiveBase.metadata.create_all)
    async with AsyncSession(engine) as session:
        session.add(
            ArchivePreviewModel(
                file_id='689665f9-eb57-4029-9fb4-526ce743d1c9',
                archive_preview='{"script.py": {"filename": "script.py", "size": 2550, '
                '"is_dir": false}, "dir2": {"is_dir": true, "script2.py": '
                '{"filename": "script2.py", "size": 1219, "is_dir": false}}}',
            )
        )
        await session.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(ArchiveBase.metadata.drop_all)


@pytest.fixture
def fake():
    fake = Faker()
    yield fake


@pytest.fixture
def redis():
    yield FakeRedis()


@pytest.fixture
def cache(redis):
    from dependencies import Cache

    yield Cache(redis)


@pytest.fixture
async def test_client_resource(redis) -> AsyncClient:
    from dependencies.cache import Cache
    from dependencies.cache import CacheInstance

    async def replace_cache():
        return Cache(redis)

    from app import create_app

    app = create_app()
    app.dependency_overrides[CacheInstance.get_cache] = replace_cache
    async with AsyncClient(app=app, base_url='https://') as client:
        yield client

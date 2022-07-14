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
from contextlib import contextmanager
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.command import downgrade
from alembic.command import upgrade
from alembic.config import Config
from async_asgi_testclient import TestClient
from faker import Faker
from fakeredis.aioredis import FakeRedis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from dependencies.cache import Cache
from dependencies.cache import CacheInstance
from models.api_archive_sql import ArchivePreviewModel
from resources.db import get_db_session


@contextmanager
def chdir(directory: Path) -> None:
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture(scope='session')
def project_root() -> Path:
    path = Path(__file__)

    while path.name != 'dataops':
        path = path.parent

    yield path


@pytest.fixture(scope='session')
def db_uri(project_root) -> str:
    with PostgresContainer('postgres:9.5') as postgres:
        database_uri = postgres.get_connection_url().replace('+psycopg2', '+asyncpg')
        config = Config('migrations/alembic.ini')
        with chdir(project_root):
            config.set_main_option('database_uri', database_uri)
            upgrade(config, 'head')
            yield database_uri
            downgrade(config, 'base')


@pytest_asyncio.fixture
async def db_engine(db_uri):
    engine = create_async_engine(db_uri)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncSession:
    session = AsyncSession(bind=db_engine, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture
async def setup_archive_table(db_session):
    archive_row = ArchivePreviewModel(
        file_id='689665f9-eb57-4029-9fb4-526ce743d1c9',
        archive_preview='{"script.py": {"filename": "script.py", "size": 2550, '
        '"is_dir": false}, "dir2": {"is_dir": true, "script2.py": '
        '{"filename": "script2.py", "size": 1219, "is_dir": false}}}',
    )
    db_session.add(archive_row)
    await db_session.commit()
    yield


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    asyncio.set_event_loop_policy(None)


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


@pytest_asyncio.fixture
async def test_client(db_session, redis):
    async def replace_cache():
        return Cache(redis)

    from app import create_app

    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[CacheInstance.get_cache] = replace_cache
    async with TestClient(app) as client:
        yield client

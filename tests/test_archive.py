# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General
# Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from api.api_archive.archive import DatabaseConnection

file_id = 'ca852835-706b-4fb5-898d-6fcbfbf87160'
file_id_db = '689665f9-eb57-4029-9fb4-526ce743d1c9'

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def test_client_db(engine):
    SessionLocal = sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=engine)

    async def get_db_session() -> AsyncSession:
        async with SessionLocal() as session:
            yield session

    from app import create_app

    app = create_app()
    app.dependency_overrides[DatabaseConnection.get_db_session] = get_db_session
    async with TestClient(app) as client:
        yield client


async def test_v1_create_preview_return_200(test_client_db, create_db_archive):
    payload = {
        'file_id': file_id,
        'archive_preview': {"test.py": {"filename": "test.py", "size": 1111,
                "is_dir": False}, "dir2": {"is_dir": True, "test2.py":
                {"filename": "test22.py", "size": 999, "is_dir": False}}},
    }

    result = await test_client_db.post('/v1/archive', json=payload)
    res = result.json()
    assert result.status_code == 200
    assert res['result'] == 'success'


async def test_v1_create_preview_duplicate_entry_return_409(test_client_db, create_db_archive):
    payload = {
        'file_id': file_id_db,
        'archive_preview': {"test.py": {"filename": "test.py", "size": 1111,
                "is_dir": False}},
    }
    result = await test_client_db.post('/v1/archive', json=payload)
    res = result.json()
    assert result.status_code == 409
    assert res['result'] == 'Duplicate entry for preview'


async def test_v1_get_preview_return_200(test_client_db, create_db_archive):
    payload = {
        'file_id': file_id_db,
    }
    result = await test_client_db.get('/v1/archive', query_string=payload)
    res = result.json()
    assert result.status_code == 200
    assert res['result'] == {
        'script.py': {'filename': 'script.py', 'size': 2550, 'is_dir': False},
        'dir2': {'is_dir': True, 'script2.py': {'filename': 'script2.py', 'size': 1219, 'is_dir': False}},
    }


async def test_v1_get_preview_geid_not_found_return_404(test_client_db, create_db_archive):
    payload = {
        'file_id': file_id,
    }
    result = await test_client_db.get('/v1/archive', query_string=payload)
    res = result.json()
    assert result.status_code == 404
    assert res['result'] == 'Archive preview not found'


async def test_v1_delete_preview_return_200(test_client_db, create_db_archive):
    payload = {
        'file_id': file_id_db,
    }
    result = await test_client_db.delete('/v1/archive', json=payload)
    assert result.status_code == 200

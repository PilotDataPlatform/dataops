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

import json

import pytest

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def create_fake_job(monkeypatch):
    from resources.redis import SrvAioRedisSingleton

    record = {
        'session_id': '12345',
        'label': 'testlabel',
        'task_id': '5678',
        'source': '/path/to/file',
        'job_id': 'fake_global_entity_id',
        'action': 'data_transfer',
        'status': 'TRANSFER',
        'code': 'any',
        'operator': 'me',
        'progress': 'SUCCESS',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': None,
        },
        'update_timestamp': '1643041442',
    }

    async def fake_return(x, y):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(SrvAioRedisSingleton, 'mget_by_prefix', fake_return)


@pytest.fixture
async def create_fake_job_response(monkeypatch):
    from resources.redis import SrvAioRedisSingleton

    async def fake_return(x, y):
        return b''

    monkeypatch.setattr(SrvAioRedisSingleton, 'mget_by_prefix', fake_return)


@pytest.fixture
async def create_fake_job_delete_response(monkeypatch):
    from resources.redis import SrvAioRedisSingleton

    async def fake_return(x, y):
        return b''

    monkeypatch.setattr(SrvAioRedisSingleton, 'mdele_by_prefix', fake_return)


@pytest.fixture
async def fake_job_save_status(monkeypatch):
    from resources.redis import SrvAioRedisSingleton

    record = {
        'session_id': '12345',
        'label': 'testlabel',
        'source': 'any',
        'task_id': '5678',
        'job_id': 'fake_global_entity_id',
        'action': 'data_transfer',
        'status': 'TRANSFER',
        'code': 'any',
        'operator': 'me',
        'progress': 'SUCCESS',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': None,
        },
        'update_timestamp': '1643041442',
    }

    async def fake_return(x, y, z):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(SrvAioRedisSingleton, 'set_by_key', fake_return)


@pytest.fixture
async def create_fake_job_updated(monkeypatch):
    from resources.redis import SrvAioRedisSingleton

    record = {
        'session_id': '12345',
        'label': 'testlabel',
        'task_id': '5678',
        'source': '/path/to/file',
        'job_id': 'fake_global_entity_id',
        'action': 'data_transfer',
        'status': 'TRANSFER',
        'code': 'any',
        'operator': 'me',
        'progress': 'SUCCESS',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': 'newgeid',
        },
        'update_timestamp': '1643041442',
    }

    async def fake_return(x, y):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(SrvAioRedisSingleton, 'mget_by_prefix', fake_return)


@pytest.fixture
async def fake_job_save_status_updated_task(monkeypatch):
    from resources.redis import SrvAioRedisSingleton

    record = {
        'session_id': '12345',
        'label': 'testlabel',
        'source': 'any',
        'task_id': '5678',
        'job_id': 'fake_global_entity_id',
        'action': 'data_transfer',
        'status': 'TRANSFER',
        'code': 'any',
        'operator': 'me',
        'progress': 'SUCCESS',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': 'newgeid',
        },
        'update_timestamp': '1643041442',
    }

    async def fake_return(x, y, z):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(SrvAioRedisSingleton, 'set_by_key', fake_return)


async def test_v1_create_new_redis_task_return_200(test_client, create_fake_job_response, fake_job_save_status):
    payload = {
        'session_id': '12345',
        'task_id': '5678',
        'job_id': 'fake_global_entity_id',
        'source': 'any',
        'action': 'data_transfer',
        'target_status': 'TRANSFER',
        'project_geid': 'any',
        'operator': 'me',
        'progress': 0,
        'code': 'testcode',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': None,
        },
        'update_timestamp': '1643041440',
    }
    response = await test_client.post('/v1/tasks/', json=payload)
    res = response.json()['result']
    assert response.status_code == 200
    assert res == 'SUCCEED'


async def test_v1_create_new_redis_task_with_duplicate_job_id_return_500(test_client, create_fake_job):
    payload = {
        'session_id': '12345',
        'task_id': '5678',
        'job_id': 'fake_global_entity_id',
        'source': 'any',
        'action': 'data_transfer',
        'target_status': 'TRANSFER',
        'project_geid': 'any',
        'operator': 'me',
        'progress': 0,
        'code': 'testcode',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': None,
        },
        'update_timestamp': '1643041440',
    }
    response = await test_client.post('/v1/tasks/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 500
    assert 'job id already exists: fake_global_entity_id' in res


async def test_v1_get_redis_task_return_200(test_client, create_fake_job):
    payload = {
        'session_id': '12345',
        'label': 'Container',
        'job_id': 'fake_global_entity_id',
        'code': 'testcode',
        'action': 'data_transfer',
        'operator': 'me',
        'source': 'any',
    }
    response = await test_client.get('/v1/tasks/', query_string=payload)
    res = response.json()['result'][0]
    assert res['session_id'] == '12345'
    assert res['progress'] == 'SUCCESS'
    assert res['update_timestamp'] == '1643041442'
    assert response.status_code == 200


async def test_v1_delete_redis_task_return_200(test_client, create_fake_job_delete_response):
    payload = {
        'session_id': '12345',
        'label': 'Container',
        'job_id': 'fake_global_entity_id',
        'code': 'testcode',
        'action': 'data_transfer',
        'operator': 'me',
        'source': 'any',
    }
    response = await test_client.delete('/v1/tasks/', json=payload)
    res = response.json()['result']
    assert response.status_code == 200
    assert res == 'SUCCEED'


async def test_v1_update_redis_task_return_200(test_client, create_fake_job_updated, fake_job_save_status_updated_task):
    payload = {
        'session_id': '12345',
        'label': 'Container',
        'job_id': 'fake_global_entity_id',
        'progress': 1,
        'status': 'SUCCEED',
        'add_payload': {'parent_folder_geid': 'newgeid'},
    }
    response = await test_client.put('/v1/tasks/', json=payload)
    res = response.json()['result']
    assert response.status_code == 200
    assert res['payload']['parent_folder_geid'] == 'newgeid'

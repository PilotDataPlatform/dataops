# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not, see
# http://www.gnu.org/licenses/.

import json

import pytest

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def create_fake_job_response(monkeypatch):
    from resources.redis import SrvAioRedisSingleton

    async def fake_return(x, y):
        return b''

    monkeypatch.setattr(SrvAioRedisSingleton, 'mget_by_prefix', fake_return)


@pytest.fixture
async def fake_job_save_status(monkeypatch):
    from resources.redis import SrvAioRedisSingleton

    record = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'job_id': '0cf78578-1bbf-4cd8-b256-3adcdaafd761-1649278991',
        'source_id': '776dc0a8b',
        'include_ids': ['112233'],
        'project': 'testproject',
        'request_id': '',
        'generic': True,
        'operator': 'admin',
        'destination_id': '886dc0a8b',
        'auth_token': {'at': None, 'rt': None},
        'create_timestamp': '1649278991.118386',
    }

    async def fake_return(x, y, z):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(SrvAioRedisSingleton, 'set_by_key', fake_return)


async def test_v1_create_copy_file_operation_job_return_202(
    test_client, httpx_mock, create_fake_job_response, fake_job_save_status
):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/776dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false'}},
    )

    # validate destination
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/886dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false'}},
    )

    # validate target
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/112233/',
        status_code=200,
        json={'result': {'id': '112233', 'name': 'file.py', 'type': 'file', 'archived': 'false'}},
    )

    # send message to queue
    httpx_mock.add_response(
        method='POST',
        url='http://queue_service/v1/send_message',
        status_code=200,
        json={},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': '112233'}], 'source': '776dc0a8b', 'destination': '886dc0a8b'},
        'operator': 'admin',
        'operation': 'copy',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['result'][0]
    assert response.status_code == 202
    assert res['session_id'] == 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33'
    assert res['payload']['source'] == '776dc0a8b'
    assert res['payload']['destination'] == '886dc0a8b'
    assert res['payload']['targets'][0] == '112233'


async def test_v1_create_copy_file_operation_job_with_invalid_source_return_500(test_client, httpx_mock):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/invalid/',
        status_code=200,
        json={'result': {}},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': '112233'}], 'source': 'invalid', 'destination': '886dc0a8b'},
        'operator': 'admin',
        'operation': 'copy',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 500
    assert 'Not found resource: invalid' in res


async def test_v1_create_copy_file_operation_job_with_invalid_destination_return_500(test_client, httpx_mock):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/776dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false'}},
    )

    # validate destination
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/invalid/',
        status_code=200,
        json={'result': {}},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': '112233'}], 'source': '776dc0a8b', 'destination': 'invalid'},
        'operator': 'admin',
        'operation': 'copy',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 500
    assert 'Not found resource: invalid' in res


async def test_v1_create_copy_file_operation_job_with_invalid_target_resource_return_500(test_client, httpx_mock):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/776dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false'}},
    )

    # validate destination
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/886dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false'}},
    )

    # validate target
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/invalid/',
        status_code=200,
        json={'result': {}},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': 'invalid'}], 'source': '776dc0a8b', 'destination': '886dc0a8b'},
        'operator': 'admin',
        'operation': 'copy',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 500
    assert 'Not found resource: invalid' in res


async def test_v1_create_copy_file_operation_job_with_target_resource_is_archived_return_400(test_client, httpx_mock):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/776dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false'}},
    )

    # validate destination
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/886dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false'}},
    )

    # validate target
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/112233/',
        status_code=200,
        json={'result': {'id': '112233', 'name': 'file.py', 'type': 'file', 'archived': True}},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': '112233'}], 'source': '776dc0a8b', 'destination': '886dc0a8b'},
        'operator': 'admin',
        'operation': 'copy',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 400
    assert 'Error occurred' in res


async def test_v1_create_copy_file_operation_job_with_target_resource_invalid_resource_return_400(
    test_client, httpx_mock
):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/776dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': False}},
    )

    # validate destination
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/886dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': False}},
    )

    # validate target
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/112233/',
        status_code=200,
        json={'result': {'id': '112233', 'name': 'file.py', 'type': 'container', 'archived': False}},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': '112233'}], 'source': '776dc0a8b', 'destination': '886dc0a8b'},
        'operator': 'admin',
        'operation': 'copy',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 400
    assert 'Error occurred' in res


async def test_v1_create_delete_file_operation_job_return_202(
    test_client, httpx_mock, create_fake_job_response, fake_job_save_status
):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/776dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false', 'zone': 0}},
    )

    # validate target
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/112233/',
        status_code=200,
        json={'result': {'id': '112233', 'name': 'file.py', 'type': 'file', 'archived': 'false', 'zone': 0}},
    )

    # send message to queue
    httpx_mock.add_response(
        method='POST',
        url='http://queue_service/v1/send_message',
        status_code=200,
        json={},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': '112233'}], 'source': '776dc0a8b'},
        'operator': 'admin',
        'operation': 'delete',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['result'][0]
    assert response.status_code == 202
    assert res['session_id'] == 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33'


async def test_v1_create_delete_file_operation_job_with_target_resource_not_found_return_500(
    test_client, httpx_mock, create_fake_job_response, fake_job_save_status
):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/776dc0a8b/',
        status_code=200,
        json={'result': {'name': 'amammoliti', 'type': 'name_folder', 'archived': 'false', 'zone': 0}},
    )

    # validate target
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/121212/',
        status_code=200,
        json={'result': {}},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': '121212'}], 'source': '776dc0a8b'},
        'operator': 'admin',
        'operation': 'delete',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 500
    assert 'Not found resource: 121212' in res


async def test_v1_create_delete_file_operation_job_with_invalid_source_return_400(
    test_client, httpx_mock, create_fake_job_response, fake_job_save_status
):
    # validate source
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/121212/',
        status_code=200,
        json={'result': {}},
    )

    payload = {
        'session_id': 'admin-e17e19b3-b6a5-4198-9458-1c1a67a98a33',
        'task_id': 'default_task_id',
        'payload': {'targets': [{'id': '555555'}], 'source': '121212'},
        'operator': 'admin',
        'operation': 'delete',
        'project_code': 'testproject',
    }
    response = await test_client.post('/v1/files/actions/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 500
    assert 'Not found resource: 121212' in res

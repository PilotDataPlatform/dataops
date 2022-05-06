# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for
# more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not, see
# http://www.gnu.org/licenses/.

import pytest


@pytest.mark.parametrize('operation', ['read', 'write'])
async def test_lock(test_client_resource, fake, operation):
    payload = {
        'resource_key': fake.pystr(),
        'operation': operation,
    }

    response = await test_client_resource.post('/v2/resource/lock/', json=payload)
    assert response.status_code == 200

    response = await test_client_resource.delete('/v2/resource/lock/', json=payload)
    assert response.status_code == 200


@pytest.mark.parametrize('operation', ['read', 'write'])
async def test_bulk_lock_performs_lock_for_multiple_keys(test_client_resource, fake, operation):
    key1 = f'a_{fake.pystr()}'
    key2 = f'b_{fake.pystr()}'
    payload = {
        'resource_keys': [key1, key2],
        'operation': operation,
    }

    response = await test_client_resource.post('/v2/resource/lock/bulk', json=payload)
    assert response.status_code == 200

    expected_result = [
        [key1, True],
        [key2, True],
    ]
    result = response.json()['result']

    assert expected_result == result


@pytest.mark.parametrize('operation', ['read', 'write'])
async def test_bulk_lock_stops_locking_when_lock_attempt_fails(test_client_resource, fake, operation):
    key1 = f'a_{fake.pystr()}'
    key2 = f'b_{fake.pystr()}'
    key3 = f'c_{fake.pystr()}'

    await test_client_resource.post('/v2/resource/lock/', json={'resource_key': key2, 'operation': 'write'})

    payload = {
        'resource_keys': [key1, key2, key3],
        'operation': operation,
    }

    response = await test_client_resource.post('/v2/resource/lock/bulk', json=payload)
    assert response.status_code == 409

    expected_result = [
        [key1, True],
        [key2, False],
        [key3, False],
    ]
    result = response.json()['result']

    assert expected_result == result


@pytest.mark.parametrize('operation', ['read', 'write'])
async def test_bulk_unlock_performs_unlock_for_multiple_keys(test_client_resource, fake, operation):
    key1 = f'a_{fake.pystr()}'
    key2 = f'b_{fake.pystr()}'

    for key in [key1, key2]:
        await test_client_resource.post('/v2/resource/lock/', json={'resource_key': key, 'operation': 'write'})

    payload = {
        'resource_keys': [key1, key2],
        'operation': operation,
    }

    response = await test_client_resource.delete('/v2/resource/lock/bulk', json=payload)
    assert response.status_code == 200

    expected_result = [
        [key1, True],
        [key2, True],
    ]
    result = response.json()['result']

    assert expected_result == result


@pytest.mark.parametrize('operation', ['read', 'write'])
async def test_bulk_unlock_continues_unlocking_when_unlock_attempt_fails(test_client_resource, fake, operation):
    key1 = f'a_{fake.pystr()}'
    key2 = f'b_{fake.pystr()}'

    await test_client_resource.post('/v2/resource/lock/', json={'resource_key': key2, 'operation': 'write'})

    payload = {
        'resource_keys': [key1, key2],
        'operation': operation,
    }

    response = await test_client_resource.delete('/v2/resource/lock/bulk', json=payload)
    assert response.status_code == 400

    expected_result = [
        [key1, False],
        [key2, True],
    ]
    result = response.json()['result']

    assert expected_result == result


@pytest.mark.parametrize('operation', ['read', 'write'])
async def test_lock_returns_404_for_not_existing_lock(test_client_resource, fake, operation):
    payload = {
        'resource_key': fake.pystr(),
        'operation': operation,
    }

    response = await test_client_resource.delete('/v2/resource/lock/', json=payload)
    assert response.status_code == 400


async def test_read_lock_not_exist_after_multiple_lock_unlock_operations(test_client_resource, fake):
    payload = {
        'resource_key': fake.pystr(),
        'operation': 'read',
    }

    num = 10
    for _ in range(num):
        response = await test_client_resource.post('/v2/resource/lock/', json=payload)
        assert response.status_code == 200

    for _ in range(num):
        response = await test_client_resource.delete('/v2/resource/lock/', json=payload)
        assert response.status_code == 200

    response = await test_client_resource.get('/v2/resource/lock/', params=payload)
    status = response.json()['result']['status']
    assert status is None


async def test_second_write_lock_is_not_allowed_and_returns_409(test_client_resource, fake):
    payload = {
        'resource_key': fake.pystr(),
        'operation': 'write',
    }

    response = await test_client_resource.post('/v2/resource/lock/', json=payload)
    assert response.status_code == 200

    response = await test_client_resource.post('/v2/resource/lock/', json=payload)
    assert response.status_code == 409

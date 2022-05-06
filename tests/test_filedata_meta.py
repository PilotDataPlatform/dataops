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

import pytest

collection_geid = 'abc123'

pytestmark = pytest.mark.asyncio


async def test_v1_create_filedata_return_200(test_client, httpx_mock):
    # create atlas entry
    httpx_mock.add_response(
        method='POST',
        url='http://cataloguing_service/v2/filedata',
        status_code=200,
        json={'result': {'mutatedEntities': {'CREATE': [{'guid': '123atlas'}]}}},
    )

    # create file entity in metadata service
    httpx_mock.add_response(
        method='POST',
        url='http://metadata_service/v1/item/',
        status_code=200,
        json={'result': {'id': '2'}},
    )

    payload = {
        'uploader': 'admin',
        'file_name': 'test_create.txt',
        'file_size': 12793,
        'description': '',
        'namespace': 'greenroom',
        'labels': ['123', 'test'],
        'project_code': 'project123',
        'dcm_id': 'BCD-1234_2',
        'parent_folder_geid': '',
        'bucket': 'bucket',
        'minio_object_path': '/minio/path',
        'version_id': '11',
    }
    response = await test_client.post('/v1/filedata/', json=payload)
    assert response.status_code == 200


async def test_v1_create_filedata_failed_to_create_entity_return_500(test_client, httpx_mock):
    # create atlas entry
    httpx_mock.add_response(
        method='POST',
        url='http://cataloguing_service/v2/filedata',
        status_code=200,
        json={'result': {'mutatedEntities': {'CREATE': [{'guid': '123atlas'}]}}},
    )

    # create file entity in metadata service
    httpx_mock.add_response(
        method='POST',
        url='http://metadata_service/v1/item/',
        status_code=500,
        json={},
    )

    payload = {
        'uploader': 'admin',
        'file_name': 'test_create.txt',
        'file_size': 12793,
        'description': '',
        'namespace': 'greenroom',
        'labels': ['123', 'test'],
        'project_code': 'project123',
        'dcm_id': 'BCD-1234_2',
        'parent_folder_geid': '',
        'bucket': 'bucket',
        'minio_object_path': '/minio/path',
        'version_id': '11',
    }
    response = await test_client.post('/v1/filedata/', json=payload)
    res = response.json()['error_msg']
    assert response.status_code == 500
    assert 'Fail to create metadata in postgres' in res


async def test_v1_create_filedata_failed_to_update_apache_atlas_return_500(test_client, httpx_mock):

    # create atlas entry
    httpx_mock.add_response(
        method='POST',
        url='http://cataloguing_service/v2/filedata',
        status_code=500,
        json={},
    )

    payload = {
        'uploader': 'admin',
        'file_name': 'test_create.txt',
        'file_size': 12793,
        'description': '',
        'namespace': 'greenroom',
        'labels': ['123', 'test'],
        'project_code': 'project123',
        'dcm_id': 'BCD-1234_2',
        'parent_folder_geid': '',
        'bucket': 'bucket',
        'minio_object_path': '/minio/path',
        'version_id': '11',
    }
    response = await test_client.post('/v1/filedata/', json=payload)
    assert response.status_code == 500

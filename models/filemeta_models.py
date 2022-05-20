# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

from pydantic import BaseModel
from pydantic import Field

from models.base_models import APIResponse

# FiledataMeta


class FiledataMetaPOST(BaseModel):
    uploader: str
    file_name: str
    file_size: int
    namespace: str
    labels: list
    project_code: str
    parent_folder_geid: str = ''
    # Minio attribute
    bucket: str = ''
    minio_object_path: str = ''
    version_id: str = ''


class FiledataMetaPOSTResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'id': '85465212-168a-4f0c-a7aa-f3a19795d2ff',
            'parent': '28c608ac-1693-4318-a1c4-412caf2cd74a',
            'parent_path': 'path.to.file',
            'type': 'file',
            'zone': 0,
            'name': 'filename',
            'size': 0,
            'owner': 'username',
            'container_code': 'project_code',
            'container_type': 'project',
            'created_time': '2022-04-13 13:30:10.890347',
            'last_updated_time': '2022-04-13 13:30:10.890347',
            'storage': {
                'id': 'ba623005-8183-419a-972a-e4ce0d539349',
                'location_uri': 'https://example.com/item',
                'version': '1.0',
            },
            'extended': {
                'id': 'dc763d28-7e74-4db3-a702-fa719aa702c6',
                'extra': {
                    'tags': ['tag1', 'tag2'],
                    'system_tags': ['tag1', 'tag2'],
                    'attributes': {'101778d7-a628-41ea-823b-e4b377f3476c': {'key1': 'value1', 'key2': 'value2'}},
                },
            },
        },
    )

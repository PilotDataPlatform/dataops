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

from config import ConfigClass
from models.base_models import APIResponse

# FiledataMeta


class FiledataMetaPOST(BaseModel):
    uploader: str
    file_name: str
    file_size: int
    namespace: str
    labels: list
    project_code: str
    dcm_id: str = ''
    parent_folder_geid: str = ''
    # Minio attribute
    bucket: str = ''
    minio_object_path: str = ''
    version_id: str = ''


class FiledataMetaPOSTResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'archived': False,
            'file_size': 1024,
            'full_path': '/data/storage/dcm/raw/BCD-1234_file_2.aacn',
            'dcm_id': 'BCD-1234_2',
            'guid': '5321880a-1a41-4bc8-a5d5-9767323205792',
            'id': 478,
            'labels': [ConfigClass.CORE_ZONE_LABEL, 'File', 'Processed'],
            'name': 'BCD-1234_file_2.aacn',
            'namespace': 'core',
            'path': '/data/storage/dcm/raw',
            'process_pipeline': 'greg_testing',
            'time_created': '2021-01-06T18:02:55',
            'time_lastmodified': '2021-01-06T18:02:55',
            'type': 'processed',
            'uploader': 'admin',
            'operator': 'admin',
        },
    )

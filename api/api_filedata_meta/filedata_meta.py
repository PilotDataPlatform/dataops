# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero
# General Public License as published by the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.

import uuid

import httpx
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from logger import LoggerFactory

from config import ConfigClass
from models import filemeta_models as models
from resources.cataloguing_manager import CataLoguingManager
from resources.error_handler import catch_internal

router = APIRouter()


@cbv(router)
class FiledataMeta:
    def __init__(self):
        self._logger = LoggerFactory('api_file_meta').get_logger()

    @router.post('/', response_model=models.FiledataMetaPOSTResponse, summary='Create or Update filedata meta')
    @catch_internal('api_file_meta')
    async def post(self, data: models.FiledataMetaPOST):
        api_response = models.FiledataMetaPOSTResponse()
        self._logger.info('Metadata request received')
        cata_mgr = CataLoguingManager()

        # fetch global entity id
        geid = str(uuid.uuid4())
        # create atlas entity
        await cata_mgr.create_file_meta(data, geid)

        zone_mapping = {'greenroom': 0}.get(data.namespace, 1)

        data = {
            'id': geid,
            'parent': data.parent_folder_geid,
            'parent_path': data.minio_object_path.replace('/', '.'),
            'type': 'file',
            'zone': zone_mapping,
            'name': data.file_name,
            'size': data.file_size,
            'owner': data.uploader,
            'container_code': data.project_code,
            'container_type': 'project',
            'location_uri': 'minio://%s/%s/%s' % (ConfigClass.MINIO_SERVICE, data.bucket, data.minio_object_path),
            'version': data.version_id,
            'tags': data.labels,
            'dcm_id': data.dcm_id,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(ConfigClass.METADATA_SERVICE + 'item/', json=data, timeout=10)
            if response.status_code != 200:
                raise Exception('Fail to create metadata in postgres: %s' % (response.__dict__))
            api_response.result = response.json().get('result', {})

        return api_response.json_response()

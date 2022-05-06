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

import httpx

from config import ConfigClass
from models import filemeta_models as models


class CataLoguingManager:
    base_url = ConfigClass.CATALOGUING_SERVICE_V2

    async def create_file_meta(self, post_form: models.FiledataMetaPOST, geid):
        filedata_endpoint = 'filedata'
        req_postform = {
            'uploader': post_form.uploader,
            'file_name': post_form.file_name,
            'path': post_form.minio_object_path,
            'file_size': post_form.file_size,
            'description': '',
            'namespace': post_form.namespace,
            'project_code': post_form.project_code,
            'labels': post_form.labels,
            'global_entity_id': geid,
            'operator': post_form.uploader,
            'processed_pipeline': '',
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(json=req_postform, url=self.base_url + filedata_endpoint, timeout=None)
        if res.status_code == 200:
            json_payload = res.json()
            created_entity = None
            if json_payload['result']['mutatedEntities'].get('CREATE'):
                created_entity = json_payload['result']['mutatedEntities']['CREATE'][0]
            elif json_payload['result']['mutatedEntities'].get('UPDATE'):
                created_entity = json_payload['result']['mutatedEntities']['UPDATE'][0]
            if created_entity:
                guid = created_entity['guid']
                return {'guid': guid}
            else:
                return {'error_code': 500, 'result': json_payload}
        else:
            json_payload = res.json()
            return {'error_code': res.status_code, 'result': json_payload}

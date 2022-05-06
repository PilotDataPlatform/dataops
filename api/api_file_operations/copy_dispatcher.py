# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero
# General Public License as published by the Free Software Foundation, either version 3 of the License, or any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.

import time
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import httpx

from api.api_file_operations.dispatcher import BaseDispatcher
from config import ConfigClass
from models import file_ops_models as models
from models.base_models import EAPIResponseCode
from resources.helpers import fetch_geid
from resources.redis_project_session_job import SessionJob


class CopyDispatcher(BaseDispatcher):
    """Validate targets, create copy file/folder sessions and send messages to the queue."""

    async def execute(
        self, _logger, data: models.FileOperationsPOST, auth_token: Dict[str, str]
    ) -> Tuple[EAPIResponseCode, Union[str, List[Dict[str, Any]]]]:
        """Execute copy logic."""

        if not await self.is_valid_folder(data.payload.source):
            return EAPIResponseCode.bad_request, f'Invalid source: {data.payload.source}'

        if not await self.is_valid_folder(data.payload.destination):
            return EAPIResponseCode.bad_request, f'Invalid destination: {data.payload.destination}'

        try:
            targets = await self.validate_targets(data.payload.targets)
        except ValueError as e:
            return EAPIResponseCode.bad_request, str(e)

        job_geid = fetch_geid()
        session_job = SessionJob(
            data.session_id, data.project_code, 'data_transfer', data.operator, task_id=data.task_id
        )

        try:
            await session_job.set_job_id(job_geid)
            session_job.set_progress(0)
            session_job.set_source(', '.join(targets.names))
            session_job.set_status(models.EActionState.RUNNING.name)
            session_job.add_payload('source', data.payload.source)
            session_job.add_payload('destination', data.payload.destination)
            session_job.add_payload('targets', list(targets.ids))
            payload = {
                'event_type': 'folder_copy',
                'payload': {
                    'session_id': data.session_id,
                    'job_id': job_geid,
                    'source_geid': data.payload.source,
                    'include_geids': list(targets.ids),
                    'project': data.project_code,
                    'request_id': str(data.payload.request_id or ''),
                    'generic': True,
                    'operator': data.operator,
                    'destination_geid': data.payload.destination,
                    'auth_token': auth_token,
                },
                'create_timestamp': time.time(),
            }
            _logger.info('Sending Message To Queue: ' + str(payload))
            async with httpx.AsyncClient() as client:
                response = await client.post(url=ConfigClass.SEND_MESSAGE_URL, json=payload)
            _logger.info(f'Message To Queue has been sent: {response.text}')
            await session_job.save()
        except Exception as e:
            exception_message = str(e)
            session_job.set_status(models.EActionState.TERMINATED.name)
            session_job.add_payload('error', exception_message)
            await session_job.save()

        return EAPIResponseCode.accepted, [session_job.to_dict()]

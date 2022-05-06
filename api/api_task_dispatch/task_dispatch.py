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

from common import LoggerFactory
from fastapi import APIRouter
from fastapi_utils.cbv import cbv

from models import task_dispatch as models
from models.base_models import APIResponse
from models.base_models import EAPIResponseCode
from resources.error_handler import catch_internal
from resources.redis_project_session_job import SessionJob
from resources.redis_project_session_job import session_job_delete_status
from resources.redis_project_session_job import session_job_get_status

router = APIRouter()


@cbv(router)
class TaskDispatcher:
    def __init__(self):
        self._logger = LoggerFactory('api_task_dispatch').get_logger()

    @router.post(
        '/',
        response_model=models.TaskDispatchPOSTResponse,
        summary='Asynchronized Task Management API, Create a new task',
    )
    @catch_internal('api_task_dispatch')
    async def post(self, data: models.TaskDispatchPOST):
        api_response = APIResponse()
        session_job = SessionJob(
            data.session_id, data.code, data.action, data.operator, label=data.label, task_id=data.task_id
        )
        await session_job.set_job_id(data.job_id)
        session_job.set_progress(data.progress)
        session_job.set_source(data.source)
        for key in data.payload:
            session_job.add_payload(key, data.payload[key])
        session_job.set_status('INIT')
        await session_job.save()
        api_response.code = EAPIResponseCode.success
        api_response.result = 'SUCCEED'
        return api_response.json_response()

    @router.get('/', summary='Asynchronized Task Management API, Get task information')
    @catch_internal('api_task_dispatch')
    async def get(self, session_id, label='Container', job_id='*', code='*', action='*', operator='*'):
        api_response = APIResponse()
        fetched = await session_job_get_status(session_id, label, job_id, code, action, operator)

        # here sort the list by timestamp in descending order
        def get_update_time(x):
            return x.get('update_timestamp', 0)

        fetched.sort(key=get_update_time, reverse=True)

        api_response.code = EAPIResponseCode.success
        api_response.result = fetched

        return api_response.json_response()

    @router.delete('/', summary='Asynchronized Task Management API, Delete tasks')
    @catch_internal('api_task_dispatch')
    async def delete(self, data: models.TaskDispatchDELETE):
        api_response = APIResponse()
        await session_job_delete_status(data.session_id, data.label, data.job_id, data.code, data.action, data.operator)
        api_response.code = EAPIResponseCode.success
        api_response.result = 'SUCCEED'
        return api_response.json_response()

    @router.put('/', summary='Asynchronized Task Management API, Update tasks')
    @catch_internal('api_task_dispatch')
    async def put(self, data: models.TaskDispatchPUT):
        api_response = APIResponse()
        my_job = await SessionJob.load(data.session_id, '*', '*', '*', label=data.label, job_id=data.job_id)
        for k, v in data.add_payload.items():
            my_job.add_payload(k, v)
        my_job.set_progress(data.progress)
        my_job.set_status(data.status)
        await my_job.save()
        api_response.code = EAPIResponseCode.success
        api_response.result = my_job.to_dict()
        return api_response.json_response()

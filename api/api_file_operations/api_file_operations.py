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

from typing import Optional

from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Header
from fastapi_utils.cbv import cbv

from api.api_file_operations.copy_dispatcher import CopyDispatcher
from api.api_file_operations.delete_dispatcher import DeleteDispatcher
from models import file_ops_models as models
from models.base_models import APIResponse
from models.base_models import EAPIResponseCode
from resources.error_handler import catch_internal

router = APIRouter()


@cbv(router)
class FileOperations:
    def __init__(self):
        self._logger = LoggerFactory('api_file_operations').get_logger()

    @router.post(
        '/',
        response_model=models.FileOperationsPOSTResponse,
        summary='File operations api, invoke an async file operation job',
    )
    @catch_internal('api_file_operations')
    async def post(
        self,
        data: models.FileOperationsPOST,
        authorization: Optional[str] = Header(None),
        refresh_token: Optional[str] = Header(None),
    ):
        token = {
            'at': authorization,
            'rt': refresh_token,
        }

        self._logger.info(f'Request tokens: {token}.')

        job_dispatcher = {
            'copy': CopyDispatcher,
            'delete': DeleteDispatcher,
        }.get(data.operation, None)

        api_response = APIResponse()

        if not job_dispatcher:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = 'Invalid operation'
            return api_response.json_response()
        code, result = await job_dispatcher().execute(self._logger, data, token)
        api_response.code = code
        if not api_response.code == EAPIResponseCode.accepted:
            api_response.error_msg = 'Error occurred'
        api_response.result = result

        return api_response.json_response()

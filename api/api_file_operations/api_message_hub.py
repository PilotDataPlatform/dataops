# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.

from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from logger import LoggerFactory

from models import file_ops_models as models
from models.base_models import APIResponse
from models.base_models import EAPIResponseCode
from resources.error_handler import catch_internal
from resources.redis import SrvAioRedisSingleton

router = APIRouter()


@cbv(router)
class MessageHub:
    def __init__(self):
        self._logger = LoggerFactory('api_message_hub').get_logger()

    @router.post('/', response_model=models.MessageHubPOSTResponse, summary='Used for dev debugging purpose')
    @catch_internal('api_file_operations')
    async def post(self, data: models.MessageHubPOST):
        api_response = APIResponse()
        redis_connector = SrvAioRedisSingleton()
        self._logger.info('[Message received] ' + data.message)
        await redis_connector.publish(data.channel, data.message)
        api_response.result = 'succeed'
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

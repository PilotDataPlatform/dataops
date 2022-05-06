# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General
# Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.

from fastapi import APIRouter

from api.api_archive import archive
from api.api_file_operations import api_file_operations
from api.api_file_operations import api_message_hub
from api.api_filedata_meta import filedata_meta
from api.api_resource_lock import api_file_lock
from api.api_task_dispatch import task_dispatch

api_router = APIRouter()
api_router.include_router(filedata_meta.router, prefix='/filedata', tags=['filedata'])
api_router.include_router(task_dispatch.router, prefix='/tasks', tags=['task-management'])
api_router.include_router(api_file_operations.router, prefix='/files/actions', tags=['file-operations'])
api_router.include_router(api_message_hub.router, prefix='/files/actions/message', tags=['file-actions-message-hub'])

api_router.include_router(archive.router, prefix='', tags=['archive'])

api_router_v2 = APIRouter()
api_router_v2.include_router(api_file_lock.router, prefix='/resource/lock', tags=['resource-lock'])

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

from pydantic import BaseModel
from pydantic import Field

from models.base_models import APIResponse


class TaskModel(BaseModel):
    key: str = ''
    session_id: str = ''
    task_id: str = ''
    start_timestamp: str = ''
    end_timestamp: str = ''
    frontend_state: str = 'uploading'
    state: str = 'init'
    progress: float = 0.0
    file_name: str = ''
    project_code: str = ''
    project_id: str = ''


class StatusUploadResponse(APIResponse):
    """Delete file upload response class."""

    result: dict = Field(
        {}, example={'code': 200, 'error_msg': '', 'result': {'Session id deleted:' 'admin-a183jcalt13'}}
    )

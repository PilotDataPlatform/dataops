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

import json

from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from models.api_archive import ArchiveDELETERequest
from models.api_archive import ArchiveGETRequest
from models.api_archive import ArchiveGETResponse
from models.api_archive import ArchivePOSTRequest
from models.api_archive import ArchivePOSTResponse
from models.api_archive_sql import ArchivePreviewModel
from models.base_models import APIResponse
from models.base_models import EAPIResponseCode
from resources.db_connection import DatabaseConnection

router = APIRouter()


@cbv(router)
class ArchiveList:
    _logger = LoggerFactory('api_archive').get_logger()
    database_connection = DatabaseConnection

    @router.get('/archive', response_model=ArchiveGETResponse, summary='Get a zip preview given file id')
    async def get(
        self, data: dict = Depends(ArchiveGETRequest), db: AsyncSession = Depends(database_connection.get_db_session)
    ):
        """Get a Zip preview."""
        file_id = data.file_id

        self._logger.info('Get zip preview for: ' + str(file_id))
        api_response = ArchiveGETResponse()

        query = await db.execute(select(ArchivePreviewModel).filter_by(file_id=file_id))
        archive_model = query.scalars().first()
        if not archive_model:
            self._logger.info(f'Preview not found for file_id: {file_id}')
            api_response.code = EAPIResponseCode.not_found
            api_response.result = 'Archive preview not found'
            return api_response.json_response()
        api_response.result = json.loads(archive_model.archive_preview)
        return api_response.json_response()

    @router.post('/archive', response_model=ArchivePOSTResponse, summary='Create a zip preview')
    async def post(self, data: ArchivePOSTRequest, db: AsyncSession = Depends(database_connection.get_db_session)):
        """Create a ZIP preview given a file_id and preview as a dict."""
        file_id = data.file_id
        archive_preview = json.dumps(data.archive_preview)
        self._logger.info('POST zip preview for: ' + str(file_id))
        api_response = ArchivePOSTResponse()
        try:
            query = await db.execute(select(ArchivePreviewModel).filter_by(file_id=file_id))
            query_result = query.scalars().first()
            if query_result:
                self._logger.info(f'Duplicate entry for file_id: {file_id}')
                api_response.code = EAPIResponseCode.conflict
                api_response.result = 'Duplicate entry for preview'
                return api_response.json_response()

            archive_model = ArchivePreviewModel(file_id=file_id, archive_preview=archive_preview)
            db.add(archive_model)
            await db.commit()
        except Exception as e:
            self._logger.error('Psql error: ' + str(e))
            api_response.error_msg = 'Psql error: ' + str(e)
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
        api_response.result = 'success'
        return api_response.json_response()

    @router.delete('/archive', summary='Delete a zip preview, only used for unit tests')
    async def delete(self, data: ArchiveDELETERequest, db: AsyncSession = Depends(database_connection.get_db_session)):
        """Delete preview given a file_id."""
        file_id = data.file_id
        self._logger.info('DELETE zip preview for: ' + str(file_id))
        api_response = APIResponse()
        try:
            query = await db.execute(select(ArchivePreviewModel).filter_by(file_id=file_id))
            archive_model = query.scalars().first()
            await db.delete(archive_model)
            await db.commit()
        except Exception as e:
            self._logger.error('Psql error: ' + str(e))
            api_response.error_msg = 'Psql error: ' + str(e)
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
        api_response.result = 'success'
        return api_response.json_response()

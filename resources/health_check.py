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

from common import LoggerFactory
from fastapi import Depends
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine

from config import ConfigClass
from resources.db import get_db_engine
from resources.redis import SrvAioRedisSingleton

logger = LoggerFactory('api_health').get_logger()


def get_table_names(conn):
    inspector = inspect(conn)
    return inspector.get_table_names()


async def rds_check(engine: AsyncEngine = Depends(get_db_engine)):
    try:
        async with engine.connect() as conn:
            tables = await conn.run_sync(get_table_names)
        if ConfigClass.RDS_TABLE_NAME in tables:
            return True
        else:
            raise ValueError(f'RDS table {ConfigClass.RDS_TABLE_NAME} not found')
    except Exception as e:
        logger.error(f'RDS health check failed: {e}')
        return False


async def redis_check():
    try:
        redis_con = SrvAioRedisSingleton()
        if await redis_con.ping():
            return True
    except Exception as e:
        logger.error(f'Redis health check failed: {e}')
        return False

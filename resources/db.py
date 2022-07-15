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

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from config import ConfigClass


class CreateEngine:
    def __init__(self) -> None:
        self.instance = None

    async def __call__(self) -> AsyncEngine:
        """Return an instance of AsyncEngine class."""
        if not self.instance:
            self.instance = create_async_engine(
                f'postgresql+asyncpg://{ConfigClass.RDS_USERNAME}:{ConfigClass.RDS_PASSWORD}@{ConfigClass.RDS_HOST}:'
                f'{ConfigClass.RDS_PORT}/{ConfigClass.RDS_NAME}',
                echo=ConfigClass.RDS_ECHO_SQL_QUERIES,
            )

        return self.instance


get_db_engine = CreateEngine()


async def get_db_session(engine: AsyncEngine = Depends(get_db_engine)) -> AsyncSession:
    """Create a FastAPI callable dependency for SQLAlchemy AsyncSession instance."""
    session = AsyncSession(bind=engine, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()

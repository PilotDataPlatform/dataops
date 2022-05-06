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

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from config import ConfigClass


class CreateEngine:
    @staticmethod
    def get_connections():
        engine = create_async_engine(ConfigClass.RDS_DB_URI)
        SessionLocal = sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=engine)
        return SessionLocal


get_session = CreateEngine().get_connections()


class DatabaseConnection:
    @staticmethod
    async def get_db_session() -> AsyncSession:
        async with get_session() as session:
            yield session

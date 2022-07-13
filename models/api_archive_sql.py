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

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from config import ConfigClass

Base = declarative_base()


class ArchivePreviewModel(Base):
    __tablename__ = ConfigClass.RDS_TABLE_NAME
    __table_args__ = {'schema': ConfigClass.RDS_SCHEMA}
    id = Column(Integer, unique=True, primary_key=True)
    file_id = Column(UUID(as_uuid=True))
    archive_preview = Column(String())

    def __init__(self, file_id, archive_preview):
        self.file_id = file_id
        self.archive_preview = archive_preview

    def to_dict(self):
        result = {}
        for field in ['id', 'file_id', 'archive_preview']:
            result[field] = str(getattr(self, field))
        return result

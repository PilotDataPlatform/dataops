# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero
# General Public License as published by the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.

from enum import Enum
from enum import unique
from typing import Any
from typing import Dict
from typing import List
from typing import Set

from models.file_ops_models import FileOperationTarget
from resources.helpers import get_resource_by_id
from resources.helpers import get_resource_type


@unique
class ResourceType(str, Enum):
    NAME_FOLDER = 'name_folder'
    FILE = 'file'
    FOLDER = 'folder'
    CONTAINER = 'container'


class Item(dict):
    """Store information about one item from metadata service."""

    @property
    def id(self) -> str:
        return self['id']

    @property
    def name(self) -> str:
        return self['name']


class ItemList(list):
    """Store list of Items."""

    def __init__(self, items: List[Dict[str, Any]]) -> None:
        super().__init__([Item(item) for item in items])

    @property
    def ids(self) -> Set[str]:
        return {item.id for item in self}

    @property
    def names(self) -> List[str]:
        return [item.name for item in self]

    def _get_by_resource_type(self, resource_type: ResourceType) -> List[Item]:
        return [source for source in self if source['type'] == resource_type]

    def filter_folders(self) -> List[Item]:
        """Return sources with folder resource type."""
        return self._get_by_resource_type(ResourceType.FOLDER)

    def filter_files(self) -> List[Item]:
        """Return sources with file resource type."""
        return self._get_by_resource_type(ResourceType.FILE)


class BaseDispatcher:
    """Base class for all dispatcher implementations."""

    async def is_valid_folder(self, item_id: str) -> bool:
        resource = await get_resource_by_id(item_id)
        resource_type = get_resource_type([resource['type']])
        if resource_type in [ResourceType.NAME_FOLDER, ResourceType.FOLDER, ResourceType.CONTAINER]:
            return True

        return False

    async def validate_targets(self, targets: List[FileOperationTarget]) -> ItemList:
        fetched = []
        for target in targets:
            source = await get_resource_by_id(target.id)
            if not source:
                raise ValueError(f'Not found resource: {target.id}')
            if source['archived'] is True:
                raise ValueError(f'Archived files should not perform further file actions: {target.id}')
            resource_type = get_resource_type([source['type']])
            if resource_type not in [ResourceType.FILE, ResourceType.FOLDER]:
                raise ValueError(f'Invalid target type (only support File or Folder): {source}')
            fetched.append(source)
        return ItemList(fetched)

    def execute(self, *args, **kwds):
        raise NotImplementedError

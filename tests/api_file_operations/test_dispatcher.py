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

import random
import time
import uuid
from typing import Any
from typing import Callable

import pytest

from api.api_file_operations.dispatcher import Item
from api.api_file_operations.dispatcher import ItemList
from api.api_file_operations.dispatcher import ResourceType


def get_timestamp() -> int:
    """Return current timestamp."""

    return round(time.time())


@pytest.fixture
def create_item(fake) -> Callable[..., Item]:
    def _create_item(
        id_=None,
        name=None,
        resource_type=None,
        **kwds: Any,
    ) -> Item:
        if id_ is None:
            id_ = f'{uuid.uuid4()}-{get_timestamp()}'

        if name is None:
            name = fake.word()

        if resource_type is None:
            resource_type = random.choice(list(ResourceType))

        return Item(
            {
                'id': id_,
                'name': name,
                'type': resource_type,
                **kwds,
            }
        )

    return _create_item


class TestItem:
    def test_id_returns_item_id(self, create_item):
        item = create_item()
        expected_id = item['id']

        assert item.id == expected_id

    def test_name_returns_item_name(self, create_item):
        item = create_item()
        expected_name = item['name']

        assert item.name == expected_name


class TestItemList:
    def test_new_instance_converts_list_values_into_source_instances(self):
        items = ItemList([{'key': 'value'}])

        assert isinstance(items[0], Item)

    def test_ids_returns_set_with_all_item_ids(self, create_item):
        item_1 = create_item()
        item_2 = create_item()
        items = ItemList([item_1, item_2])
        expected_ids = {item_1.id, item_2.id}

        assert expected_ids == items.ids

    def test_names_returns_list_with_all_item_names(self, create_item):
        item_1 = create_item()
        item_2 = create_item()
        items = ItemList([item_1, item_2])
        expected_names = [item_1.name, item_2.name]

        assert expected_names == items.names

    def test_filter_folders_returns_sources_with_folder_resource_type(self, create_item):
        expected_item = create_item(resource_type=ResourceType.FOLDER)

        sources = ItemList([create_item(resource_type=ResourceType.FILE), expected_item])

        assert sources.filter_folders() == [expected_item]

    def test_filter_files_returns_sources_with_file_resource_type(self, create_item):
        expected_item = create_item(resource_type=ResourceType.FILE)
        sources = ItemList([create_item(resource_type=ResourceType.FOLDER), expected_item])

        assert sources.filter_files() == [expected_item]

# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

import re
from typing import Optional

import httpx
from common import GEIDClient

from config import ConfigClass


def fetch_geid():
    client = GEIDClient()
    geid = client.get_GEID()
    return geid


async def get_resource_by_id(item_id: str) -> Optional[dict]:
    """Get the item from metadata service by id.

    raise exception if the id does not exist.
    """
    url = f'{ConfigClass.METADATA_SERVICE}item/{item_id}/'
    async with httpx.AsyncClient() as client:
        request = await client.get(url)
    resource = request.json()['result']

    if not resource:
        raise Exception('Not found resource: ' + item_id)

    return resource


def get_resource_type(labels: list):
    """Get resource type."""
    resources = ['file', 'name_folder', 'folder', 'container']
    for label in labels:
        if label in resources:
            return label
    return None


def location_decoder(location: str):
    """decode resource location return ingestion_type, ingestion_host, ingestion_path."""
    splits_loaction = location.split('://', 1)
    ingestion_type = splits_loaction[0]
    ingestion_url = splits_loaction[1]
    path_splits = re.split(r'(?<!/)/(?!/)', ingestion_url, 1)
    ingestion_host = path_splits[0]
    ingestion_path = path_splits[1]
    return ingestion_type, ingestion_host, ingestion_path

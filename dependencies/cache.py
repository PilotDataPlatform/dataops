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

from typing import Optional
from typing import Union

from aioredis.client import Redis
from fastapi import Depends

from config import Settings
from config import get_settings


class GetRedis:
    """Create a FastAPI callable dependency for Redis single instance."""

    def __init__(self) -> None:
        self.instance = None

    async def __call__(self, settings: Settings = Depends(get_settings)) -> Redis:
        """Return an instance of Redis class."""

        if not self.instance:
            self.instance = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
            )
        return self.instance


get_redis = GetRedis()


class Cache:
    """Manage cache entries."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def set(self, key: str, value: Union[str, bytes]) -> bool:
        """Set the value for the key."""

        return await self.redis.set(key, value)

    async def get(self, key: str) -> Optional[bytes]:
        """Return the value for the key or None if the key doesn't exist."""

        return await self.redis.get(key)

    async def delete(self, key: str) -> bool:
        """Delete the value for the key.

        Return true if the key existed before the removal.
        """

        return bool(await self.redis.delete(key))

    async def is_exist(self, key: str) -> bool:
        """Return true if the value for the key exists."""
        return bool(await self.redis.exists(key))


class CacheInstance:
    @staticmethod
    async def get_cache(redis: Redis = Depends(get_redis)) -> Cache:
        """Return an instance of Cache class."""

        return Cache(redis)

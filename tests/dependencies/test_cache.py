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

import pytest
from aioredis import Redis

from config import get_settings
from dependencies import Cache
from dependencies.cache import CacheInstance
from dependencies.cache import GetRedis


@pytest.fixture
def get_redis():
    yield GetRedis()


class TestGetRedis:
    async def test_instance_has_uninitialized_instance_attribute_after_creation(self, get_redis):
        assert get_redis.instance is None

    async def test_call_returns_an_instance_of_redis(self, get_redis):
        redis = await get_redis(settings=get_settings())
        assert redis is get_redis.instance
        assert isinstance(redis, Redis)


class TestCache:
    async def test_get_cache_returns_an_instance_of_cache(self, redis):
        cache = await CacheInstance.get_cache(redis=redis)
        assert isinstance(cache, Cache)

    async def test_set_stores_value_by_key(self, fake, cache):
        key = fake.pystr()
        value = fake.binary(10)

        result = await cache.set(key, value)
        assert result is True

        result = await cache.get(key)
        assert result == value

    async def test_get_returns_value_by_key(self, fake, cache):
        key = fake.pystr()
        value = fake.binary(10)
        await cache.set(key, value)

        result = await cache.get(key)
        assert result == value

    async def test_get_returns_none_if_key_does_not_exist(self, fake, cache):
        key = fake.pystr()

        result = await cache.get(key)
        assert result is None

    async def test_delete_removes_value_by_key(self, fake, cache):
        key = fake.pystr()
        value = fake.pystr()
        await cache.set(key, value)

        result = await cache.delete(key)
        assert result is True

        result = await cache.get(key)
        assert result is None

    async def test_delete_returns_false_if_key_did_not_exist(self, fake, cache):
        key = fake.pystr()

        result = await cache.delete(key)
        assert result is False

    async def test_is_exist_returns_true_if_key_exists(self, fake, cache):
        key = fake.pystr()
        value = fake.pystr()
        await cache.set(key, value)

        result = await cache.is_exist(key)
        assert result is True

    async def test_is_exist_returns_false_if_key_does_not_exist(self, fake, cache):
        key = fake.pystr()

        result = await cache.is_exist(key)
        assert result is False

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

import json
from datetime import timedelta

from aioredis import StrictRedis

from config import ConfigClass


class SrvAioRedisSingleton:
    __instance = {}

    def __init__(self):
        self.host = ConfigClass.REDIS_HOST
        self.port = ConfigClass.REDIS_PORT
        self.db = ConfigClass.REDIS_DB
        self.pwd = ConfigClass.REDIS_PASSWORD
        self.connect()

    def connect(self):
        if self.__instance:
            pass
        else:
            self.__instance = StrictRedis(host=self.host, port=self.port, db=self.db, password=self.pwd)

    async def get_by_key(self, key: str):
        return await self.__instance.get(key)

    async def set_by_key(self, key: str, content: str):
        res = await self.__instance.set(key, content, ex=timedelta(hours=24))
        return res

    async def mget_by_prefix(self, prefix: str):
        query = '{}:*'.format(prefix)
        keys = await self.__instance.keys(query)
        return await self.__instance.mget(keys)

    async def get_by_prefix(self, prefix: str):
        query = '*:{}:*'.format(prefix)
        keys = await self.__instance.keys(query)
        return keys

    async def check_by_key(self, key: str):
        return await self.__instance.exists(key)

    async def delete_by_key(self, key: str):
        return await self.__instance.delete(key)

    async def unlink_by_key(self, key: str):
        return await self.__instance.unlink(key)

    async def mdele_by_prefix(self, prefix: str):
        query = '{}:*'.format(prefix)
        keys = await self.__instance.keys(query)
        results = []
        for key in keys:
            res = await self.delete_by_key(key)
            results.append(res)
        return results

    async def get_by_pattern(self, key: str, pattern: str):
        query_string = '{}:*{}*'.format(key, pattern)
        keys = await self.__instance.keys(query_string)
        return await self.__instance.mget(keys)

    async def publish(self, channel, data):
        res = await self.__instance.publish(channel, data)
        return res

    async def subscriber(self, channel):
        p = await self.__instance.pubsub()
        p.subscribe(channel)
        return p

    async def file_get_status(self, file_path):
        query = '*:{}'.format(file_path)
        keys = await self.__instance.keys(query)
        result = await self.__instance.mget(keys)

        current_action = None

        decoded_result = []
        for record in result:
            record = record.decode('utf-8')
            info = json.loads(record)
            decoded_result.append(info)

        if len(decoded_result) > 0:
            latest_item = max(decoded_result, key=lambda x: x['update_timestamp'])
            if latest_item['status'] == 'SUCCEED' or latest_item['status'] == 'TERMINATED':
                return current_action
            else:
                return latest_item['action']

        return current_action

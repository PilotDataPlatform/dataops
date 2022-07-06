# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for
# more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.

from functools import lru_cache
from typing import Any
from typing import Dict
from typing import Optional

from common import VaultClient
from pydantic import BaseSettings
from pydantic import Extra


class VaultConfig(BaseSettings):
    """Store vault related configuration."""

    APP_NAME: str = 'service_dataops_utility'
    CONFIG_CENTER_ENABLED: bool = False

    VAULT_URL: Optional[str]
    VAULT_CRT: Optional[str]
    VAULT_TOKEN: Optional[str]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    config = VaultConfig()

    if not config.CONFIG_CENTER_ENABLED:
        return {}

    client = VaultClient(config.VAULT_URL, config.VAULT_CRT, config.VAULT_TOKEN)
    return client.get_from_vault(config.APP_NAME)


class Settings(BaseSettings):
    """Store service configuration settings."""

    APP_NAME: str = 'service_dataops_utility'
    VERSION = '0.3.0'
    PORT: int = 5063
    HOST: str = '127.0.0.1'
    env: str = ''
    namespace: str = ''

    GREEN_ZONE_LABEL: str = 'Greenroom'
    CORE_ZONE_LABEL: str = 'Core'

    AUTH_SERVICE: str
    CATALOGUING_SERVICE: str
    QUEUE_SERVICE: str
    SEND_MESSAGE_URL: str
    METADATA_SERVICE: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str

    RDS_DB_URI: str
    RDS_SCHEMA_DEFAULT: str
    RDS_ECHO_SQL_QUERIES: bool = False

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_HTTPS: bool = False

    OPEN_TELEMETRY_ENABLED: bool = False
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    def __init__(self):
        super().__init__()

        self.AUTH_SERVICE = self.AUTH_SERVICE + '/v1/'
        self.CATALOGUING_SERVICE_V2 = self.CATALOGUING_SERVICE + '/v2/'
        self.QUEUE_SERVICE = self.QUEUE_SERVICE + '/v1/'
        self.SEND_MESSAGE_URL = self.SEND_MESSAGE_URL + '/v1/send_message'
        self.MINIO_SERVICE = 'http://' + self.MINIO_ENDPOINT
        self.RDS_DB_URI = self.RDS_DB_URI.replace('postgresql', 'postgresql+asyncpg')
        self.METADATA_SERVICE = self.METADATA_SERVICE + '/v1/'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, load_vault_settings, init_settings, file_secret_settings


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigClass = get_settings()
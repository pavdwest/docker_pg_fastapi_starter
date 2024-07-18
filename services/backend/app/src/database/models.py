from enum import Enum
from functools import lru_cache

from sqlalchemy import (
    URL,
    Engine,
    create_engine,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm.decl_api import DeclarativeMeta


class DatabaseDriver(str, Enum):
    ASYNC = 'postgresql+asyncpg'
    SYNC  = 'postgresql+psycopg2'
    DRIVER_ONLY = 'postgresql'


class DatabaseHost:
    def __init__(
        self,
        alias: str,
        name: str,
        username: str,
        password: str,
        port: str,
    ) -> None:
        self.alias = alias
        self.friendly_name = f"{name}"
        self.name = name
        self.username = username
        self.password = password
        self.port = port

    def clone(self):
        return DatabaseHost(
            alias=self.alias,
            name=self.name,
            username=self.username,
            password=self.password,
            port=self.port,
        )

    def __str__(self) -> str:
        from src.logging.service import logger
        return {
            'alias': self.alias,
            'friendly_name': self.friendly_name,
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'port': self.port,
        }.__str__()


class DatabaseBind:
    BaseModel = None

    def __init__(
        self,
        host: DatabaseHost,
        name: str,
        BaseModel: DeclarativeMeta,
    ) -> None:
        self.name = name
        self.BaseModel = BaseModel
        self.friendly_name = f"{host.name}/{name}"

        common_parms = {
            'username': host.username,
            'password': host.password,
            'host': host.name,
            'port': host.port,
            'database': name,
        }
        self.url_async = URL.create(
            drivername=DatabaseDriver.ASYNC,
            **common_parms,
        )
        self.url_sync = URL.create(
            drivername=DatabaseDriver.SYNC,
            **common_parms,
        )
        self.url = self.create_url(
            **common_parms,
        )
        self.host = host
        self.engine_async: AsyncEngine = None
        self.engine_sync: Engine = None

    @classmethod
    def create_url(
        cls,
        username: str,
        password: str,
        host: str,
        port: str,
        database: str,
        drivername: str = '',
    ) -> str:
        if not drivername == '':
            drivername = f"+{drivername}"
        return f"postgresql{drivername}://{username}:{password}@{host}:{port}/{database}"


    @lru_cache(maxsize=1)
    def get_engine_async(self) -> AsyncEngine:
        if self.engine_async is None:
            self.engine_async = create_async_engine(self.url_async, echo=False)
        return self.engine_async

    @lru_cache(maxsize=1)
    def get_engine_sync(self) -> AsyncEngine:
        if self.engine_sync is None:
            self.engine_sync = create_engine(self.url_sync, echo=False)
        return self.engine_sync

    def clone(self):
        return DatabaseBind(
            host=self.host.clone(),
            name=self.name,
            BaseModel=self.BaseModel,
        )

    async def shutdown(self):
        if self.engine_async is not None:
            await self.engine_async.dispose()
        if self.engine_sync is not None:
            self.engine_sync.dispose()

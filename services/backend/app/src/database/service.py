from time import sleep
from contextlib import asynccontextmanager
from functools import cache, lru_cache
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.exc import ProgrammingError

from src.config import (
    DATABASE_RETRY_LIMIT,
    DATABASE_RETRY_BACKOFF_SECONDS,
)
from src.logging.service import logger
from src.database.models import DatabaseBind, DatabaseHost


SharedBase: DeclarativeMeta = declarative_base()


class DatabaseManager:
    def init(
        self,
        DATABASE_host_name: str,
        DATABASE_host_username: str,
        DATABASE_host_password: str,
        DATABASE_name: str,
        DATABASE_host_port: str,
    ):
        # Cache the shared database host
        self.DATABASE_host = DatabaseHost(
            alias='DATABASE_HOST',
            name=DATABASE_host_name,
            username=DATABASE_host_username,
            password=DATABASE_host_password,
            port=DATABASE_host_port,
        )

        # Ensure shared db exists and create tables
        for i in range(DATABASE_RETRY_LIMIT):
            try:
                self.DATABASE_bind = self.create_db(self.DATABASE_host, DATABASE_name, SharedBase)
                self._create_models(db=self.DATABASE_bind)
                break
            except Exception as e:
                logger.error(f"Could not initialize shared database. Retrying in {DATABASE_RETRY_BACKOFF_SECONDS} seconds...")
                logger.error(e)
                sleep(DATABASE_RETRY_BACKOFF_SECONDS)

    @lru_cache(maxsize=1)
    def get_DATABASE_bind(self) -> DatabaseBind:
        return self.DATABASE_bind

    def create_db(self, host: DatabaseHost, name: str, base_model) -> DatabaseBind:
        bind = DatabaseBind(host, name, base_model)
        if not database_exists(bind.url_sync):
            logger.warning(f"Database '{bind.friendly_name}' does not exist. Creating...")
            create_database(url=bind.url_sync)

            # Verify
            if not database_exists(url=bind.url_sync):
                raise Exception('COULD NOT CREATE DATABASE!')
            else:
                logger.warning('Database created.')
        else:
            logger.info(f"Database '{bind.friendly_name}' already exists. Nothing to do.")
        return bind

    def drop_db(self, db: DatabaseBind):
        from psycopg2.errors import InvalidCatalogName
        try:
            drop_database(url=db.url_sync)
            logger.warning(f"Database '{db.url_sync}' dropped.")
        except ProgrammingError as e:
            if isinstance(e.orig, InvalidCatalogName):
                logger.warning(f"Database '{db.friendly_name}' does not exist. Nothing to do.")
            else:
                raise e

    def _create_models(self, db: DatabaseBind):
        from src.helpers import models_importer
        logger.warning(f"Syncing models and tables for {db.friendly_name}...")
        db.BaseModel.metadata.create_all(db.get_engine_sync())
        logger.warning('Synced models and tables.')

    def async_session_generator(self, engine: AsyncEngine):
        return async_sessionmaker(bind=engine)

    @asynccontextmanager
    async def session(self, db: DatabaseBind) -> AsyncIterator[AsyncSession]:
        try:
            async_session = self.async_session_generator(engine=db.get_engine_async())

            async with async_session() as session:
                yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def shutdown(self):
        await self.DATABASE_bind.shutdown()


db = DatabaseManager()

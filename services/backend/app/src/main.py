from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.logging.service import logger
from src import config
from src.app import init_app
from src.database.service import db
from src.modules.home.routes import router as home_router


# Init db
db.init(
    DATABASE_host_name=config.DATABASE_HOST_NAME,
    DATABASE_host_username=config.DATABASE_HOST_USERNAME,
    DATABASE_host_password=config.DATABASE_HOST_PASSWORD,
    DATABASE_name=config.DATABASE_NAME,
    DATABASE_host_port=config.DATABASE_HOST_PORT,
)


# App Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Startup...')
    yield
    logger.info('Shutdown...')
    # await db.close()


# Create app instance
app = init_app(lifespan)

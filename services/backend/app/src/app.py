from typing import Any, Generator

from fastapi import FastAPI

from src.config import PROJECT_NAME
from src.helpers.route_manager import add_routes


def init_app(lifespan: Generator[None, Any, None] = None):
    app = FastAPI(title=f"{PROJECT_NAME} API", lifespan=lifespan)
    add_routes(app)
    return app

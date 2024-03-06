from fastapi import FastAPI
from dog_marker.database.base import create_db_and_tables


def create_app() -> FastAPI:
    app = FastAPI(title="DogMarker - API")

    bind_events(app)

    from .api.v1 import api_v1

    app.mount("/v1", api_v1)

    return app


def bind_events(app: FastAPI) -> None:
    @app.on_event("startup")
    def on_startup() -> None:
        create_db_and_tables()

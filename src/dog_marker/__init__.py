from fastapi import FastAPI, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .configs import Config
from .database.base import Base


def create_app(config: Config = Config()) -> FastAPI:
    app = FastAPI(title="DogMarker - API")

    bind_db(app, config)

    from .api.v1 import api_v1

    app.mount("/v1", api_v1)

    return app


def bind_db(app: FastAPI, config: Config) -> None:
    is_postgres = config.DATABASE_URL.startswith("postgresql")

    if is_postgres:
        engine = create_engine(
            config.DATABASE_URL, pool_size=config.POSTGRES_DB_POOL_SIZE, max_overflow=config.POSTGRES_DB_MAX_OVERFLOW
        )
    else:
        engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})

    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @app.on_event("startup")
    def on_startup() -> None:
        if config.CREATE_DB:
            if config.DATABASE_URL.startswith("postgresql"):
                from alembic.config import Config
                from alembic import command

                alembic_cfg = Config()
                alembic_cfg.set_main_option("script_location", "alembic_postgres")
                alembic_cfg.set_main_option("sqlalchemy.url", config.DATABASE_URL)
                command.upgrade(alembic_cfg, "head")

            else:
                Base.metadata.create_all(bind=engine)

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        response = Response("Internal server error", status_code=500)
        try:
            request.state.db = session_local()
            response = await call_next(request)
        finally:
            request.state.db.close()
        return response

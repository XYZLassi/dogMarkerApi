__all__ = ["Base", "create_db"]

from fastapi import FastAPI
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from dog_marker import Config

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)


def create_db(app: FastAPI, config: Config) -> sessionmaker[Session]:
    is_postgres = config.DATABASE_URL.startswith("postgresql")

    if is_postgres:
        engine = create_engine(
            config.DATABASE_URL, pool_size=config.POSTGRES_DB_POOL_SIZE, max_overflow=config.POSTGRES_DB_MAX_OVERFLOW
        )
    else:
        engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})

    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    return session_local

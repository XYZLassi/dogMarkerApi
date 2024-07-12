import os


def get_int(value: str | int) -> int:
    if isinstance(value, int):
        return value
    else:
        return int(value)


def get_int_or_none(value: str | int | None) -> int | None:
    if value is None or value == "":
        return None

    return get_int(value)


class Config:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./sql_app.db")
    CREATE_DB: bool = os.environ.get("CREATE_DB") == "1"

    POSTGRES_DB_POOL_SIZE: int = get_int(os.environ.get("POSTGRES_DB_POOL_SIZE", 20))
    POSTGRES_DB_MAX_OVERFLOW: int = get_int(os.environ.get("POSTGRES_DB_MAX_OVERFLOW", 20))

    APP_TOKEN: str | None = os.environ.get("APP_TOKEN", None)

    DELETE_TRASH_ENTRIES_AFTER_MINUTES: int | None = get_int_or_none(
        os.environ.get("DELETE_TRASH_ENTRIES_AFTER_MINUTES", None)
    )

    JOB_EXECUTE_INTERVAL_SECONDS: int = get_int(os.environ.get("JOB_EXECUTE_INTERVAL_SECONDS", 10))
    JOB_CLEANUP_INTERVAL_SECONDS: int = get_int(os.environ.get("JOB_CLEANUP_INTERVAL_SECONDS", 600))


class DevelopConfig(Config):
    pass


class TestConfig(Config):
    DATABASE_URL = "sqlite:///:memory:"

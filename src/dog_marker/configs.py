import os


class Config:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./sql_app.db")
    CREATE_DB: bool = os.environ.get("CREATE_DB") == "1"

    POSTGRES_DB_POOL_SIZE: int = int(os.environ.get("POSTGRES_DB_POOL_SIZE", "20"))
    POSTGRES_DB_MAX_OVERFLOW: int = int(os.environ.get("POSTGRES_DB_MAX_OVERFLOW", "20"))


class DevelopConfig(Config):
    pass


class TestConfig(Config):
    DATABASE_URL = "sqlite:///:memory:"

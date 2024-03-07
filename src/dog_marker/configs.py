import os


class Config:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./sql_app.db")
    CREATE_DB: bool = os.environ.get("CREATE_DB") == "1"


class DevelopConfig(Config):
    pass


class TestConfig(Config):
    DATABASE_URL = "sqlite:///:memory:"

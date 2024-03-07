import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from dog_marker import Base
from dog_marker.database.models.schemas import Entry


@pytest.fixture()
def db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def valid_entry() -> Entry:
    return Entry(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Test Entry",
        description="Hello Testing",
        image_path="https://http.cat/404",
        create_date=datetime.utcnow(),
        update_date=datetime.utcnow(),
        latitude=51.05325109503178,
        longitude=13.733939121392618,
    )

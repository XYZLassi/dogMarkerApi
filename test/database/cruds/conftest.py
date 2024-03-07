import pytest
from sqlalchemy.orm import Session

from dog_marker.database.cruds import EntryCRUD


@pytest.fixture
def entry_crud(db: Session) -> EntryCRUD:
    crud = EntryCRUD(db)
    return crud

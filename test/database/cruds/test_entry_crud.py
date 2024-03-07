import uuid

from dog_marker.database.cruds import EntryCRUD
from dog_marker.database.cruds.entry_crud import CreateEntryProtocol
from dog_marker.database.errors import DbNotFoundError


def test_create_entry(entry_crud: EntryCRUD, valid_entry: CreateEntryProtocol):
    user_id = uuid.uuid4()

    create_entry = entry_crud.create(user_id, valid_entry)

    assert create_entry.id == valid_entry.id
    assert create_entry.user_id == user_id

    assert create_entry.title == valid_entry.title
    assert create_entry.description == valid_entry.description
    assert create_entry.image_path == valid_entry.image_path
    assert create_entry.latitude == valid_entry.latitude
    assert create_entry.longitude == valid_entry.longitude
    assert create_entry.create_date == valid_entry.create_date

    return


def test_get_entry(entry_crud: EntryCRUD, valid_entry: CreateEntryProtocol):
    user_id = uuid.uuid4()
    create_entry = entry_crud.create(user_id, valid_entry)

    get_entry = entry_crud.get(create_entry.id)
    assert create_entry == get_entry


def test_get_entry_wrong_id(entry_crud: EntryCRUD, valid_entry: CreateEntryProtocol):
    user_id = uuid.uuid4()
    create_entry = entry_crud.create(user_id, valid_entry)

    try:
        get_entry = entry_crud.get(uuid.uuid4())
        assert False
    except DbNotFoundError:
        assert True
    except:
        assert False

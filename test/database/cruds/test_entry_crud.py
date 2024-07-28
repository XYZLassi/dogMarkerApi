import random
import uuid

from dog_marker.database.cruds import EntryCRUD


def test_create_entry(entry_crud: EntryCRUD):
    owner_id = uuid.uuid4()
    test_title = "Hallo Entry"

    longitude = random.uniform(-180, 180)
    latitude = random.uniform(-90, 90)

    flow = (
        entry_crud.create(owner_id, test_title)
        .map(entry_crud.set_coordinate(longitude, latitude))
        .map(entry_crud.add())
        .map(entry_crud.commit())
    )

    value = flow.ok()

    assert value
    assert value.id
    assert value.user_id == owner_id
    assert value.title == test_title
    assert value.longitude == longitude
    assert value.latitude == latitude
    assert value.warning_level == 0

    assert value.mark_to_delete is None
    assert value.description is None
    assert value.image_path is None
    assert value.image_delete_url is None
    assert value.create_date
    assert value.update_date

    return

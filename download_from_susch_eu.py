import uuid

import requests

from dog_marker.api.v1.schemas import EntrySchema
from dog_marker.database.base import create_db
from dog_marker.configs import Config
from dog_marker.database.cruds import EntryCRUD


def main():
    config = Config()
    config.CREATE_DB = True
    session_local = create_db(config)

    response = requests.get("https://dog.susch.eu/v1/entries/")
    assert response.ok

    owner_id = uuid.uuid4()

    with session_local() as session:
        entry_crud = EntryCRUD(session)
        json_values = response.json()
        if len(json_values) == 0:
            return
        for json_entry in json_values:
            try:
                entry = EntrySchema.model_validate(json_entry)

                db_entry = entry_crud.get(entry.id)
                if db_entry.is_err():
                    db_entry = entry_crud.create(owner_id, entry.title).map(entry_crud.add())

                image_path = str(entry.image_path) if entry.image_path else None
                image_delete_url = str(entry.image_delete_url) if entry.image_delete_url else None

                db_entry = (
                    db_entry.map(entry_crud.set_title(entry.title))
                    .map(entry_crud.set_description(entry.description))
                    .map(entry_crud.set_warning_level(entry.warning_level))
                    .map(entry_crud.set_coordinate(entry.longitude, entry.latitude))
                    .map(entry_crud.add_image(image_path, image_delete_url))
                    .map(entry_crud.set_create_date(entry.create_date))
                    .map(entry_crud.commit())
                )
            except Exception:
                pass


if __name__ == "__main__":
    main()

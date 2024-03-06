from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from dog_marker.database.cruds import entry_crude
from dog_marker.dtypes.coordinate import Coordinate
from ..errors import NotAuthorizedError
from ..schemas import EntrySchema, CreateEntrySchema, UpdateEntrySchema


class EntryService:
    def __init__(self, db: Session):
        self.db = db

    def get_entry(self, entry_id: UUID, owner_id: UUID | None = None) -> EntrySchema:
        entry = entry_crude.get_entry(self.db, entry_id)

        result = EntrySchema.from_orm(entry)
        result.is_owner = entry.user_id == owner_id

        return result

    def get_entries(
        self,
        user_id: UUID | None = None,
        owner_id: UUID | None = None,
        coordinate: Coordinate | None = None,
        skip: int | None = 0,
        limit: int | None = 100,
    ) -> Iterable[EntrySchema]:
        entries = entry_crude.get_entries(
            self.db,
            user_id=user_id,
            owner_id=owner_id,
            coordinate=coordinate,
            skip=skip,
            limit=limit,
        )
        for entry in entries:
            result = EntrySchema.from_orm(entry)
            result.is_owner = entry.user_id == user_id or entry.user_id == owner_id

            yield result

    def create_entry(self, user_id: UUID, entry: CreateEntrySchema) -> EntrySchema:
        new_db_entry = entry_crude.create_entry(db=self.db, user_id=user_id, **entry.dict())

        result = EntrySchema.from_orm(new_db_entry)
        result.is_owner = True
        return result

    def delete_entry(self, entry_id: UUID, user_id: UUID) -> None:
        return entry_crude.delete_entry(self.db, entry_id=entry_id, user_id=user_id)

    def update_entry(self, entry_id: UUID, user_id: UUID, update_entry: UpdateEntrySchema) -> EntrySchema:
        old_entry = entry_crude.get_entry(self.db, entry_id)

        if old_entry.user_id != user_id:
            raise NotAuthorizedError()

        entry = entry_crude.update_entry(self.db, entry_id, **update_entry.dict())

        result = EntrySchema.from_orm(entry)
        result.is_owner = old_entry.user_id == user_id
        return result

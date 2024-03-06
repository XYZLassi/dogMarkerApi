from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from dog_marker.database.cruds import EntryCRUD
from dog_marker.dtypes.coordinate import Coordinate
from ..errors import NotAuthorizedError
from ..schemas import EntryApiSchema, CreateEntryApiSchema, UpdateEntryApiSchema


class EntryService:
    def __init__(self, db: Session):
        self.entry_crud = EntryCRUD(db)

    def get(self, entry_id: UUID, owner_id: UUID | None = None) -> EntryApiSchema:
        entry = self.entry_crud.get(entry_id)
        api_entry = EntryApiSchema.from_db(entry)

        api_entry.is_owner = entry.user_id == owner_id if owner_id else False

        return api_entry

    def all(
        self,
        user_id: UUID | None = None,
        owner_id: UUID | None = None,
        coordinate: Coordinate | None = None,
        skip: int | None = 0,
        limit: int | None = 100,
    ) -> Iterable[EntryApiSchema]:
        entries = self.entry_crud.all(
            user_id=user_id,
            owner_id=owner_id,
            coordinate=coordinate,
            skip=skip,
            limit=limit,
        )
        for entry in entries:
            api_entry = EntryApiSchema.from_db(entry)

            if owner_id is not None:
                api_entry.is_owner = entry.user_id == owner_id
            elif user_id is not None:
                api_entry.is_owner = entry.user_id == user_id

            yield api_entry

    def update_entry(self, entry_id: UUID, user_id: UUID, update_entry: UpdateEntryApiSchema) -> EntryApiSchema:
        old_entry = self.entry_crud.get(entry_id)

        if old_entry.user_id != user_id:
            raise NotAuthorizedError()

        entry = self.entry_crud.update(entry_id, update_entry)

        api_entry = EntryApiSchema.from_db(entry)
        api_entry.is_owner = old_entry.user_id == user_id
        return api_entry

    def create(self, user_id: UUID, data: CreateEntryApiSchema) -> EntryApiSchema:
        entry = self.entry_crud.create(user_id, data)

        api_entry = EntryApiSchema.from_db(entry)
        api_entry.is_owner = True
        return api_entry

    def delete(self, entry_id: UUID, user_id: UUID) -> bool:
        return self.entry_crud.delete(entry_id=entry_id, user_id=user_id)

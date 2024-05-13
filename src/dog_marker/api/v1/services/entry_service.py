import datetime
from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from dog_marker.database.cruds import EntryCRUD
from dog_marker.dtypes.coordinate import Coordinate
from dog_marker.dtypes.pagination import Pagination
from ..errors import NotAuthorizedError
from ..schemas import EntrySchema, CreateEntrySchema, UpdateEntrySchema


class EntryService:
    def __init__(self, db: Session):
        self.entry_crud = EntryCRUD(db)

    def get(self, entry_id: UUID, owner_id: UUID | None = None) -> EntrySchema:
        entry = self.entry_crud.get(entry_id)
        is_owner = entry.user_id == owner_id if owner_id else False

        api_entry = EntrySchema.from_entry(entry, is_owner=is_owner)

        return api_entry

    def all(
        self,
        page_info: Pagination,
        user_id: UUID | None = None,
        owner_id: UUID | None = None,
        coordinate: Coordinate | None = None,
        date_from: datetime.datetime | None = None,
    ) -> Iterable[EntrySchema]:
        entries = self.entry_crud.all(
            user_id=user_id,
            owner_id=owner_id,
            coordinate=coordinate,
            page_info=page_info,
            date_from=date_from,
        )
        for entry in entries:
            is_owner = False
            if owner_id is not None:
                is_owner = entry.user_id == owner_id
            elif user_id is not None:
                is_owner = entry.user_id == user_id

            api_entry = EntrySchema.from_entry(entry, is_owner=is_owner)

            yield api_entry

    def update_entry(self, entry_id: UUID, user_id: UUID, update_entry: UpdateEntrySchema) -> EntrySchema:
        old_entry = self.entry_crud.get(entry_id)

        if old_entry.user_id != user_id:
            raise NotAuthorizedError()

        entry = self.entry_crud.update(entry_id, update_entry)

        api_entry = EntrySchema.from_entry(entry)
        api_entry.is_owner = old_entry.user_id == user_id
        return api_entry

    def create(self, user_id: UUID, data: CreateEntrySchema) -> EntrySchema:
        entry = self.entry_crud.create(user_id, data)

        api_entry = EntrySchema.from_entry(entry)
        api_entry.is_owner = True
        return api_entry

    def delete(self, entry_id: UUID, user_id: UUID) -> bool:
        return self.entry_crud.delete(entry_id=entry_id, user_id=user_id)

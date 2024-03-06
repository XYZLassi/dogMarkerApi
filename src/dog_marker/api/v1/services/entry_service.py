import uuid
from typing import Iterable

from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..schemas import EntrySchema, CreateEntrySchema, UpdateEntrySchema

from dog_marker.database.cruds import entry_crude


def get_entry(
    db: Session, entry_id: uuid.UUID, owner_id: uuid.UUID | None = None
) -> EntrySchema | None:
    entry = entry_crude.get_entry(db, entry_id)
    if entry is None:
        return None

    result = EntrySchema.from_orm(entry)
    result.is_owner = entry.user_id == owner_id

    return result


def get_entries(
    db: Session,
    user_id: uuid.UUID | None = None,
    owner_id: uuid.UUID | None = None,
    coord: tuple[float, float] | None = None,  # Todo: Dataclass
    skip: int | None = 0,
    limit: int | None = 100,
) -> Iterable[EntrySchema]:
    entries = entry_crude.get_entries(
        db,
        user_id=user_id,
        owner_id=owner_id,
        coord=coord,
        skip=skip,
        limit=limit,
    )
    for entry in entries:
        result = EntrySchema.from_orm(entry)
        result.is_owner = entry.user_id == user_id or entry.user_id == owner_id

        yield result


def create_entry(
    db: Session, user_id: uuid.UUID, entry: CreateEntrySchema
) -> EntrySchema:
    new_db_entry = entry_crude.create_entry(
        db=db, user_id=user_id, **entry.dict()
    )

    result = EntrySchema.from_orm(new_db_entry)
    result.is_owner = True
    return result


def delete_entry(db: Session, entry_id: uuid.UUID, user_id: uuid.UUID) -> None:
    return entry_crude.delete_entry(db, entry_id=entry_id, user_id=user_id)


def update_entry(
    db: Session,
    entry_id: uuid.UUID,
    user_id: uuid.UUID,
    update_entry: UpdateEntrySchema,
) -> EntrySchema:
    old_entry = entry_crude.get_entry(db, entry_id)
    if old_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    elif old_entry.user_id != user_id:
        raise HTTPException(status_code=401, detail="User not authorized")

    entry = entry_crude.update_entry(db, entry_id, **update_entry.dict())

    result = EntrySchema.from_orm(entry)
    result.is_owner = old_entry.user_id == user_id
    return result

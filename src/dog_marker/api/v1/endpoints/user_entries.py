import uuid
from typing import Iterable

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..schemas import EntrySchema, CreateEntrySchema, UpdateEntrySchema
from ..services import entry_service
from .dependecies import get_db

router = APIRouter()


@router.get("/{user_id}/entries")
async def get_user_entries(
    user_id: uuid.UUID, db: Session = Depends(get_db)
) -> Iterable[EntrySchema]:
    new_entry = entry_service.get_entries(db, owner_id=user_id)
    return new_entry


@router.post("/{user_id}/entries")
async def post_new_entry(
    user_id: uuid.UUID, entry: CreateEntrySchema, db: Session = Depends(get_db)
) -> EntrySchema:
    new_entry = entry_service.create_entry(db, user_id, entry)
    return new_entry


@router.put(
    "/{user_id}/entries/{entry_id}",
)
async def update_entry(
    user_id: uuid.UUID,
    entry_id: uuid.UUID,
    update_entry: UpdateEntrySchema,
    db: Session = Depends(get_db),
) -> EntrySchema:
    updated_entry = entry_service.update_entry(
        db, entry_id, user_id, update_entry
    )

    return updated_entry


@router.delete("/{user_id}/entries/{entry_id}", status_code=204)
async def delete_entry_for_user(
    user_id: uuid.UUID, entry_id: uuid.UUID, db: Session = Depends(get_db)
) -> None:
    entry_service.delete_entry(db, entry_id, user_id)

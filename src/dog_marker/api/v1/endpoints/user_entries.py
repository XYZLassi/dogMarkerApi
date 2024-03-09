from typing import Iterable
from uuid import UUID

from fastapi import APIRouter, Depends

from .dependecies import get_service
from ..schemas import EntrySchema, CreateEntrySchema, UpdateEntrySchema
from ..services import EntryService

router = APIRouter()


@router.get("/{user_id}/entries", response_model=list[EntrySchema])
async def get_user_entries(
    user_id: UUID, entry_service: EntryService = Depends(get_service(EntryService))
) -> Iterable[EntrySchema]:
    new_entry = entry_service.all(owner_id=user_id)
    return new_entry


@router.post("/{user_id}/entries", response_model=EntrySchema)
async def post_new_entry(
    user_id: UUID, entry: CreateEntrySchema, entry_service: EntryService = Depends(get_service(EntryService))
) -> EntrySchema:
    new_entry = entry_service.create(user_id, entry)
    return new_entry


@router.put("/{user_id}/entries/{entry_id}", response_model=EntrySchema)
async def put_entry(
    user_id: UUID,
    entry_id: UUID,
    update_entry: UpdateEntrySchema,
    entry_service: EntryService = Depends(get_service(EntryService)),
) -> EntrySchema:
    updated_entry = entry_service.update_entry(entry_id, user_id, update_entry)

    return updated_entry


@router.delete("/{user_id}/entries/{entry_id}", status_code=204)
async def delete_entry_for_user(
    user_id: UUID, entry_id: UUID, entry_service: EntryService = Depends(get_service(EntryService))
) -> None:
    entry_service.delete(entry_id, user_id)

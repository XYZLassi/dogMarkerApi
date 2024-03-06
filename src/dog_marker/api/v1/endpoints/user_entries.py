from typing import Iterable
from uuid import UUID

from fastapi import APIRouter, Depends

from .dependecies import get_service
from ..schemas import EntryApiSchema, CreateEntryApiSchema, UpdateEntryApiSchema
from ..services import EntryService

router = APIRouter()


@router.get("/{user_id}/entries", response_model=list[EntryApiSchema])
async def get_user_entries(
    user_id: UUID, entry_service: EntryService = Depends(get_service(EntryService))
) -> Iterable[EntryApiSchema]:
    new_entry = entry_service.all(owner_id=user_id)
    return new_entry


@router.post("/{user_id}/entries", response_model=EntryApiSchema)
async def post_new_entry(
    user_id: UUID, entry: CreateEntryApiSchema, entry_service: EntryService = Depends(get_service(EntryService))
) -> EntryApiSchema:
    new_entry = entry_service.create(user_id, entry)
    return new_entry


@router.put("/{user_id}/entries/{entry_id}", response_model=EntryApiSchema)
async def put_entry(
    user_id: UUID,
    entry_id: UUID,
    update_entry: UpdateEntryApiSchema,
    entry_service: EntryService = Depends(get_service(EntryService)),
) -> EntryApiSchema:
    updated_entry = entry_service.update_entry(entry_id, user_id, update_entry)

    return updated_entry


@router.delete("/{user_id}/entries/{entry_id}", status_code=204)
async def delete_entry_for_user(
    user_id: UUID, entry_id: UUID, entry_service: EntryService = Depends(get_service(EntryService))
) -> None:
    entry_service.delete(entry_id, user_id)

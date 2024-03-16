from typing import Iterable
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from dog_marker.dtypes.pagination import Pagination
from .dependecies import get_service, query_pagination
from ..schemas import EntrySchema, CreateEntrySchema, UpdateEntrySchema
from ..services import EntryService

router = APIRouter()


@router.get("/{user_id}/entries", response_model=list[EntrySchema], operation_id="get_user_entries")
async def get_user_entries(
    user_id: UUID,
    page_info: Pagination = Depends(query_pagination),
    entry_service: EntryService = Depends(get_service(EntryService)),
) -> Iterable[EntrySchema]:
    new_entry = entry_service.all(page_info=page_info, owner_id=user_id)
    return new_entry


@router.post("/{user_id}/entries", response_model=EntrySchema, operation_id="create_new_entry")
async def post_new_entry(
    user_id: UUID, entry: CreateEntrySchema, entry_service: EntryService = Depends(get_service(EntryService))
) -> EntrySchema:
    new_entry = entry_service.create(user_id, entry)
    return new_entry


@router.put("/{user_id}/entries/{entry_id}", response_model=EntrySchema, operation_id="update_entry")
async def put_entry(
    user_id: UUID,
    entry_id: UUID,
    update_entry: UpdateEntrySchema,
    entry_service: EntryService = Depends(get_service(EntryService)),
) -> EntrySchema:
    updated_entry = entry_service.update_entry(entry_id, user_id, update_entry)

    return updated_entry


@router.delete("/{user_id}/entries/{entry_id}", status_code=204, response_class=Response, operation_id="delete_entry")
async def delete_entry_for_user(
    user_id: UUID, entry_id: UUID, entry_service: EntryService = Depends(get_service(EntryService))
) -> None:
    entry_service.delete(entry_id, user_id)

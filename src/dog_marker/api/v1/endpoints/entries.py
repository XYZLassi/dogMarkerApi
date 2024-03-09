from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from dog_marker.dtypes.coordinate import Coordinate
from .dependecies import get_service, query_coordinate
from ..schemas import EntrySchema
from ..services import EntryService

router = APIRouter()


@router.get("/", response_model=list[EntrySchema])
async def get_all_entries(
    user_id: UUID | None = None,
    skip: int | None = 0,
    limit: int | None = 100,
    coordinate: Coordinate | None = Depends(query_coordinate),
    entry_service: EntryService = Depends(get_service(EntryService)),
):
    entries = entry_service.all(user_id=user_id, coordinate=coordinate, skip=skip, limit=limit)
    return entries


@router.get("/{entry_id}", response_model=Optional[EntrySchema])
async def get_entry_by_id(entry_id: UUID, entry_service: EntryService = Depends(get_service(EntryService))):
    entry = entry_service.get(entry_id)
    return entry

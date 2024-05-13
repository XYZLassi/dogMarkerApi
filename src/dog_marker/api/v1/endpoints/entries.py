import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from dog_marker.dtypes.coordinate import Coordinate
from dog_marker.dtypes.pagination import Pagination
from dog_marker.database.schemas import warning_levels
from .dependecies import get_service, query_coordinate, query_pagination
from ..schemas import EntrySchema

from ..services import EntryService

router = APIRouter()


@router.get("/", response_model=list[EntrySchema], operation_id="get_all_entries")
async def get_all_entries(
    user_id: UUID | None = None,
    page_info: Pagination = Depends(query_pagination),
    coordinate: Coordinate | None = Depends(query_coordinate),
    date_from: datetime.datetime | None = None,
    warning_level: warning_levels = "information",
    entry_service: EntryService = Depends(get_service(EntryService)),
):
    entries = entry_service.all(
        page_info=page_info,
        user_id=user_id,
        coordinate=coordinate,
        date_from=date_from,
        warning_level=warning_level,
    )
    return entries


@router.get("/{entry_id}", response_model=Optional[EntrySchema], operation_id="get_entry")
async def get_entry_by_id(entry_id: UUID, entry_service: EntryService = Depends(get_service(EntryService))):
    entry = entry_service.get(entry_id)
    return entry

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .dependecies import get_db
from ..schemas import EntrySchema
from ..services import entry_service

router = APIRouter()


@router.get("/", response_model=list[EntrySchema])
async def get_all_entries(
    db: Session = Depends(get_db),
    user_id: uuid.UUID | None = None,
    longitude: float | None = None,
    latitude: float | None = None,
    skip: int | None = 0,
    limit: int | None = 100,
):
    assert (
        longitude is not None and -180 <= longitude <= 180
    ), "longitude must beetween -180° to 180°"
    assert (
        latitude is not None and -180 <= longitude <= 180
    ), "latitude must beetween -90° to 90°"

    if (
        latitude is not None
        and longitude is None
        or latitude is None
        and longitude is not None
    ):
        raise HTTPException(
            status_code=418, detail="latitude and longitude must both set"
        )

    coord = (
        (longitude, latitude)
        if longitude is not None and latitude is not None
        else None
    )

    entries = entry_service.get_entries(
        db, user_id=user_id, coord=coord, skip=skip, limit=limit
    )
    return entries


@router.get("/{entry_id}", response_model=Optional[EntrySchema])
async def get_entry_by_id(entry_id: uuid.UUID, db: Session = Depends(get_db)):
    entry = entry_service.get_entry(db, entry_id)
    return entry

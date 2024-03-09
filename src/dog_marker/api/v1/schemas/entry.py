from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from dog_marker.database.schemas import Entry
from dog_marker.dtypes.coordinate import Longitude, Latitude


class EntrySchema(BaseModel):
    id: UUID
    title: str
    description: str | None
    image_path: str | None
    image_delete_url: str | None
    longitude: Longitude
    latitude: Latitude
    create_date: datetime
    update_date: datetime
    is_owner: bool = False

    @staticmethod
    def from_entry(entry: Entry) -> EntrySchema:
        return EntrySchema(**entry.dict())


class CreateEntrySchema(BaseModel):
    id: UUID | None = Field(None)
    title: str
    description: str | None = Field(None)
    image_path: str | None = Field(None)
    image_delete_url: str | None = Field(None)
    longitude: Longitude
    latitude: Latitude
    create_date: datetime | None = Field(None)


class UpdateEntrySchema(BaseModel):
    title: str
    description: str | None
    image_path: str | None
    image_delete_url: str | None
    longitude: Longitude
    latitude: Latitude

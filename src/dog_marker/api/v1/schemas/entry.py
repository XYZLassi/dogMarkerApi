from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from dog_marker.database.models.schemas import Entry
from dog_marker.dtypes.coordinate import Longitude, Latitude


class EntryApiSchema(BaseModel):
    id: UUID
    title: str
    description: str | None
    image_path: str | None
    longitude: Longitude
    latitude: Latitude
    create_date: datetime
    update_date: datetime
    is_owner: bool = False

    @staticmethod
    def from_db(entry: Entry) -> EntryApiSchema:
        return EntryApiSchema(**entry.dict())


class CreateEntryApiSchema(BaseModel):
    id: UUID | None = Field(None)
    title: str
    description: str | None = Field(None)
    image_path: str | None = Field(None)
    longitude: Longitude
    latitude: Latitude
    create_date: datetime | None = Field(None)


class UpdateEntryApiSchema(BaseModel):
    title: str
    description: str | None = Field(None)
    image_path: str | None = Field(None)
    longitude: Longitude
    latitude: Latitude

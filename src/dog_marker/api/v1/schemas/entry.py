from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, HttpUrl

from dog_marker.database.models import EntryDbModel
from dog_marker.database.schemas import warning_levels, WarningLevel
from dog_marker.dtypes.coordinate import Longitude, Latitude
from .category import CategorySchema


class EntrySchema(BaseModel):
    model_config = ConfigDict(use_enum_values=False)
    id: UUID
    title: str
    description: str | None
    image_path: HttpUrl | None
    image_delete_url: HttpUrl | None
    longitude: Longitude
    latitude: Latitude
    warning_level: warning_levels
    categories: list[str] = Field(default_factory=list)
    category_infos: list[CategorySchema] = Field(default_factory=list)
    create_date: datetime
    update_date: datetime
    is_owner: bool = False
    is_deleted: bool = False

    @staticmethod
    def from_db(entry: EntryDbModel, is_owner: bool = False) -> EntrySchema:
        return EntrySchema(
            id=entry.id,
            title=entry.title,
            description=entry.description,
            image_path=entry.image_path,
            image_delete_url=entry.image_delete_url if is_owner else None,
            longitude=entry.longitude,
            latitude=entry.latitude,
            warning_level=WarningLevel(entry.warning_level or 0).to_literal(),
            categories=[category.key for category in entry.categories],  # type: ignore[attr-defined]
            category_infos=[CategorySchema.from_db(category) for category in entry.categories],
            create_date=entry.create_date,
            update_date=entry.update_date,
            is_owner=is_owner,
            is_deleted=entry.is_deleted,
        )


class CreateEntrySchema(BaseModel):
    id: UUID | None = Field(None)
    title: str
    description: str | None = Field(None)
    image_path: HttpUrl | None = Field(None)
    image_delete_url: HttpUrl | None = Field(None)
    warning_level: warning_levels | None = Field(None)
    longitude: Longitude
    latitude: Latitude
    categories: list[str] | None = Field(None)
    create_date: datetime | None = Field(None)


class UpdateEntrySchema(BaseModel):
    title: str
    description: str | None
    image_path: HttpUrl | None
    image_delete_url: HttpUrl | None
    warning_level: warning_levels
    longitude: Longitude
    latitude: Latitude
    categories: list[str] | None = Field(None)

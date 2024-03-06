import uuid
from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime

from dog_marker.dtypes.coordinate import Longitude, Latitude


class EntrySchema(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    image_path: str | None
    longitude: Longitude
    latitude: Latitude
    create_date: datetime
    update_date: datetime
    is_owner: bool = False

    class Config:
        from_attributes = True
        orm_mode = True


class CreateEntrySchema(BaseModel):
    id: Optional[uuid.UUID] = Field(None)
    title: str
    description: Optional[str] = Field(None)
    image_path: Optional[str] = Field(None)
    longitude: Longitude
    latitude: Latitude
    create_date: Optional[datetime] = Field(None)


class UpdateEntrySchema(BaseModel):
    title: str
    description: Optional[str] = Field(None)
    image_path: Optional[str] = Field(None)
    longitude: Longitude
    latitude: Latitude

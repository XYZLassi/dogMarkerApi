import uuid
from typing import Optional

from pydantic import BaseModel, Field, AfterValidator
from datetime import datetime

from typing_extensions import Annotated


def check_longitude(value: float):
    assert -180 <= value <= 180, "longitude must be between -180° and 180°"
    return value


def check_Latitude(value: float):
    assert -90 <= value <= 90, "latitude must be between -90° and 90°"
    return value


Longitude = Annotated[float, AfterValidator(check_longitude)]
Latitude = Annotated[float, AfterValidator(check_Latitude)]


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

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from dog_marker.dtypes.coordinate import Longitude, Latitude

from .warning_level import WarningLevel


class Entry(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    image_path: str | None
    image_delete_url: str | None
    longitude: Longitude
    latitude: Latitude
    warning_level: WarningLevel = WarningLevel.information
    create_date: datetime
    update_date: datetime

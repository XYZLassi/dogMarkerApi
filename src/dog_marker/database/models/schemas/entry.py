from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from dog_marker.dtypes.coordinate import Longitude, Latitude


class Entry(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    image_path: str | None
    longitude: Longitude
    latitude: Latitude
    create_date: datetime
    update_date: datetime

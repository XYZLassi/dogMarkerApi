__all__ = ["Longitude", "Latitude", "Coordinate"]

from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated


def check_longitude(value: float):
    assert -180 <= value <= 180, "longitude must be between -180° and 180°"
    return value


def check_Latitude(value: float):
    assert -90 <= value <= 90, "latitude must be between -90° and 90°"
    return value


Longitude = Annotated[float, AfterValidator(check_longitude)]
Latitude = Annotated[float, AfterValidator(check_Latitude)]


class Coordinate(BaseModel):
    longitude: Longitude
    latitude: Latitude

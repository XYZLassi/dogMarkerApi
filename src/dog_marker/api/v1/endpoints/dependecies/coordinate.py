from dog_marker.dtypes.coordinate import Longitude, Latitude, Coordinate

from fastapi import HTTPException


def query_coordinate(longitude: Longitude | None = None, latitude: Latitude | None = None) -> Coordinate | None:
    if longitude is not None and latitude is not None:
        return Coordinate(longitude=longitude, latitude=latitude)
    if longitude is None and latitude is None:
        return None

    raise HTTPException(status_code=418, detail="latitude and longitude must both set")

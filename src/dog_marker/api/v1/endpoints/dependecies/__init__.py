__all__ = ["get_db", "get_service", "query_coordinate"]

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from typing import TypeVar, Callable

from dog_marker.dtypes.coordinate import Longitude, Latitude, Coordinate

T = TypeVar("T")


def get_db(request: Request) -> Session:
    return request.state.db


def get_service(service: Callable[[Session], T]) -> Callable[[], T]:
    def helper(db: Session = Depends(get_db)) -> T:
        return service(db)

    return helper


def query_coordinate(longitude: Longitude | None = None, latitude: Latitude | None = None) -> Coordinate | None:
    if longitude is not None and latitude is not None:
        return Coordinate(longitude=longitude, latitude=latitude)
    if longitude is None and latitude is None:
        return None

    raise HTTPException(status_code=418, detail="latitude and longitude must both set")

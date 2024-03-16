from typing import Callable, TypeVar

from fastapi import Depends
from sqlalchemy.orm import Session

from .get_db import get_db

T = TypeVar("T")


def get_service(service: Callable[[Session], T]) -> Callable[[], T]:
    def helper(db: Session = Depends(get_db)) -> T:
        return service(db)

    return helper

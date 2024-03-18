__all__ = ["Pagination", "SkipInt", "LimitInt"]

from typing import Annotated

from pydantic import BaseModel, AfterValidator


def check_skip_int(value: int):
    assert value >= 0, "skip >= 0"
    return value


def check_limit_int(value: int):
    assert 0 < value <= 100, " 0 < limit <= 100"
    return value


SkipInt = Annotated[int, AfterValidator(check_skip_int)]
LimitInt = Annotated[int, AfterValidator(check_limit_int)]


class Pagination(BaseModel):
    skip: SkipInt
    limit: LimitInt

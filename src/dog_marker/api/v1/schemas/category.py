from __future__ import annotations

from pydantic import BaseModel

from dog_marker.database.schemas import Category


class CategorySchema(BaseModel):
    key: str
    title: str
    description: str | None

    @staticmethod
    def from_db(value: Category) -> CategorySchema:
        return CategorySchema(key=value.key, title=value.title, description=value.description)

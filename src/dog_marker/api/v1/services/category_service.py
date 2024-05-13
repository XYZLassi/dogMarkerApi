from sqlalchemy.orm import Session
from typing import Iterable

from dog_marker.database.cruds import CategoryCRUD
from ..schemas import CategorySchema


class CategoryService:
    def __init__(self, db: Session):
        self.crud = CategoryCRUD(db)

    def all(self) -> Iterable[CategorySchema]:
        categories = self.crud.all()

        for category in categories:
            yield CategorySchema.from_db(category)

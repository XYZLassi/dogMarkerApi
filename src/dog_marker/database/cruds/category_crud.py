from sqlalchemy.orm import Session
from ..models import CategoryDbModel


class CategoryCRUD:
    def __init__(self, db: Session):
        self.db = db

    def all(self):
        categories = self.db.query(CategoryDbModel).all()

        for category in categories:
            # noinspection PyUnresolvedReferences
            yield category.to_schema()

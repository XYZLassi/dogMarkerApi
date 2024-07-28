from result import Err, Ok
from sqlalchemy.orm import Session

from ..errors import DbNotFoundError
from ..models.entry import EntryImageDbModel


class EntryImageCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get(self, entry_image_id: int):
        result: EntryImageDbModel | None = self.db.query(EntryImageDbModel).get(entry_image_id)
        if result is None:
            return Err(DbNotFoundError(f"Cannot find image with id {entry_image_id}"))
        return Ok(result)

    def get_all(self):
        # noinspection PyTypeChecker
        result: list[EntryImageDbModel] = self.db.query(EntryImageDbModel).all()
        return Ok(result)

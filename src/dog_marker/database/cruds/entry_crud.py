import datetime
from operator import and_, or_
from typing import Callable, Type
from uuid import UUID

from result import Result, Err, Ok
from sqlalchemy import desc, exists
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.operators import is_

from ..errors import DbNotFoundError
from ..models import EntryDbModel, CategoryDbModel, EntryImageDbModel, HiddenEntry
from ..schemas import WarningLevel, warning_levels
from ...dtypes.coordinate import Coordinate, Longitude, Latitude
from ...dtypes.pagination import Pagination


# noinspection PyMethodMayBeStatic
class EntryCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get(self, entry_id: UUID) -> Result[EntryDbModel, Exception]:
        result: EntryDbModel | None = self.db.query(EntryDbModel).get(entry_id)
        if result is None:
            return Err(DbNotFoundError(f"Cannot find entry with id {entry_id}"))
        return Ok(result)

    def get_image(self, image_id: int) -> Result[EntryImageDbModel, Exception]:
        result: EntryImageDbModel | None = self.db.query(EntryImageDbModel).get(image_id)
        if result is None:
            return Err(DbNotFoundError(f"Cannot find entry-image with id {image_id}"))
        return Ok(result)

    def query(self) -> Result[Query[Type[EntryDbModel]], Exception]:
        return Ok(self.db.query(EntryDbModel))

    def all(self, page_info: Pagination | None = None) -> Callable[[Query[Type[EntryDbModel]]], list[EntryDbModel]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> list[EntryDbModel]:
            if page_info:
                query = query.offset(page_info.skip).limit(page_info.limit)
            # noinspection PyTypeChecker
            return query.all()  # type: ignore

        return __internal

    def add(self) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            self.db.add(entry)
            return entry

        return __internal

    def delete(self, user_id: UUID) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            hidden_entry = self.db.query(HiddenEntry).filter_by(entry_id=entry.id, user_id=user_id).first()
            if not hidden_entry:
                hidden_entry = HiddenEntry(entry_id=entry.id, user_id=user_id)
                self.db.add(hidden_entry)

                if entry.user_id == user_id:
                    entry.update_date = datetime.datetime.utcnow()

            return entry

        return __internal

    def undo_delete(self, user_id: UUID) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            hidden_entry = self.db.query(HiddenEntry).filter_by(entry_id=entry.id, user_id=user_id).first()
            if hidden_entry:
                self.db.delete(hidden_entry)

                if entry.user_id == user_id:
                    entry.update_date = datetime.datetime.utcnow()
            return entry

        return __internal

    def commit(self) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            self.db.commit()
            return entry

        return __internal

    def create(self, owner_id: UUID, title: str) -> Result[EntryDbModel, Exception]:
        model = EntryDbModel(user_id=owner_id, title=title)
        return Ok(model)

    def set_title(self, title: str):
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            entry.title = title
            return entry

        return __internal

    def set_description(self, description: str | None = None) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            entry.description = description
            return entry

        return __internal

    def set_warning_level(
        self, warning_level: WarningLevel | warning_levels | None = None
    ) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            entry.warning_level = WarningLevel.from_(warning_level)
            return entry

        return __internal

    def set_coordinate(self, longitude: Longitude, latitude: Latitude) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            entry.longitude = longitude
            entry.latitude = latitude
            return entry

        return __internal

    def set_categories(self, categories: list[str] | None) -> Callable[[EntryDbModel], Result[EntryDbModel, Exception]]:
        def __internal(entry: EntryDbModel) -> Result[EntryDbModel, Exception]:
            entry.clear_categories()
            if not categories:
                return Ok(entry)
            for category_key in categories:
                category = self.db.query(CategoryDbModel).get(category_key)
                if not category:
                    return Err(DbNotFoundError(f"Cannot find category with id {category_key}"))

                entry.append_category(category)
            return Ok(entry)

        return __internal

    def add_image(self, image_path: str | None, image_delete_url: str | None) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            if entry.image_delete_url != image_delete_url or entry.image_path != image_path:
                new_entry_image = EntryImageDbModel(
                    image_path=image_path,
                    image_delete_url=image_delete_url,
                )
                entry.image_infos.append(new_entry_image)
            return entry

        return __internal

    def set_id(self, entry_id: UUID | None) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            if entry_id:
                entry.id = entry_id
            return entry

        return __internal

    def set_create_date(self, create_date: datetime.datetime | None) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            entry.create_date = create_date
            return entry

        return __internal

    def set_mark_to_delete(self) -> Callable[[EntryDbModel], EntryDbModel]:
        def __internal(entry: EntryDbModel) -> EntryDbModel:
            if entry.mark_to_delete is None:
                entry.mark_to_delete = datetime.datetime.utcnow()
            return entry

        return __internal

    def order_by_coordinate(
        self,
        coordinate: Coordinate | None = None,
    ) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            if coordinate:
                query = query.order_by(desc(EntryDbModel.calc_distance(coordinate.longitude, coordinate.latitude)))
            return query

        return __internal

    def filter_by_date_from(
        self, date_from: datetime.datetime | None = None
    ) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            if date_from is not None:
                query = query.filter(EntryDbModel.update_date >= date_from)
            return query

        return __internal

    def filter_by_warning_level(
        self, warning_level: WarningLevel | warning_levels | None = None
    ) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            level_enum = WarningLevel.from_(warning_level)
            query = query.filter(EntryDbModel.warning_level >= level_enum.value)
            return query

        return __internal

    def filter_by_user(self, user_id: UUID) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            # noinspection PyTypeChecker
            query = query.filter(EntryDbModel.user_id == user_id)
            return query

        return __internal

    def filter_show_trash(self, user_id: UUID) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            query = query.filter(
                exists().where(and_(HiddenEntry.user_id == user_id, HiddenEntry.entry_id == EntryDbModel.id))
            )
            return query

        return __internal

    def filter_show_owner_deleted(self) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            query = query.filter(
                exists().where(
                    and_(HiddenEntry.user_id == EntryDbModel.user_id, HiddenEntry.entry_id == EntryDbModel.id)
                )
            )
            return query

        return __internal

    def filter_owner_deleted(
        self, ignore_ids: list[UUID] | None = None
    ) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        ignore_ids = ignore_ids or list()

        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            query = query.filter(
                or_(
                    EntryDbModel.user_id.in_(ignore_ids),
                    ~exists().where(
                        and_(HiddenEntry.user_id == EntryDbModel.user_id, HiddenEntry.entry_id == EntryDbModel.id)
                    ),
                )
            )
            return query

        return __internal

    def filter_user_deleted(
        self, user_id: UUID | None = None
    ) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            if user_id:
                query = query.filter(
                    ~exists().where(and_(HiddenEntry.user_id == user_id, HiddenEntry.entry_id == EntryDbModel.id))
                )
            return query

        return __internal

    def filter_marked_to_delete(self) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            query = query.filter(is_(EntryDbModel.mark_to_delete, None))
            return query

        return __internal

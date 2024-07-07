import datetime
from operator import and_
from typing import Callable, Type, Iterable
from uuid import UUID

from result import Result, Err, Ok
from sqlalchemy import desc
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.functions import count

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
        result: EntryDbModel = self.db.query(EntryDbModel).get(entry_id)
        if result is None:
            return Err(DbNotFoundError(f"Cannot find entry with id {entry_id}"))
        return Ok(result)

    def query(self) -> Result[Query[Type[EntryDbModel]], Exception]:
        return Ok(self.db.query(EntryDbModel))

    def all(self, page_info: Pagination) -> Callable[[Query[Type[EntryDbModel]]], Iterable[EntryDbModel]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Iterable[EntryDbModel]:
            if page_info:
                query = query.offset(page_info.skip).limit(page_info.limit)
            # noinspection PyTypeChecker
            return query.all()

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
                    entry_id=entry.id,
                    image_path=image_path,
                    image_delete_url=image_delete_url,
                )
                # Todo: No Add
                self.db.add(new_entry_image)
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

    def filter_deleted(
        self, user_id: UUID | None = None
    ) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            user_clause = HiddenEntry.user_id == EntryDbModel.user_id
            if user_id:
                user_clause |= HiddenEntry.user_id == user_id

            query = query.join(
                HiddenEntry,
                onclause=and_(
                    HiddenEntry.entry_id == EntryDbModel.id,
                    user_clause,
                ),
                isouter=True,
            )
            # noinspection PyTypeChecker
            query = query.filter(HiddenEntry.entry_id == None)  # noqa: E711
            return query

        return __internal

    def filter_show_deleted(self, user_id: UUID) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            query = query.join(
                HiddenEntry,
                onclause=and_(
                    HiddenEntry.entry_id == EntryDbModel.id,
                    HiddenEntry.user_id == user_id,
                ),
                isouter=True,
            )
            # noinspection PyTypeChecker
            query = query.filter(HiddenEntry.entry_id != None)  # noqa: E711
            return query

        return __internal

    def filter_owner_deleted(self) -> Callable[[Query[Type[EntryDbModel]]], Query[Type[EntryDbModel]]]:
        def __internal(query: Query[Type[EntryDbModel]]) -> Query[Type[EntryDbModel]]:
            sub_query = (
                self.db.query(count(HiddenEntry.user_id).label("count"))
                .filter(HiddenEntry.user_id == EntryDbModel.user_id)
                .subquery()
            )
            query = query.filter(sub_query == 0)
            return query

        return __internal

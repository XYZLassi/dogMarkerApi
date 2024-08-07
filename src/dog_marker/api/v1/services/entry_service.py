import datetime
from typing import Callable, Iterable
from uuid import UUID

from pydantic import HttpUrl
from result import Result, Ok, Err
from sqlalchemy.orm import Session

from dog_marker.database.cruds import EntryCRUD
from dog_marker.database.models import EntryDbModel
from dog_marker.database.schemas import warning_levels
from dog_marker.dtypes.coordinate import Coordinate
from dog_marker.dtypes.pagination import Pagination
from .. import NotAuthorizedError
from ..errors import EntityNotFound
from ..schemas import EntrySchema, CreateEntrySchema, UpdateEntrySchema


# noinspection PyMethodMayBeStatic
class EntryService:
    def __init__(self, db: Session):
        self.db = db

    def check_domain(self, image_path: HttpUrl | None, image_delete_url: HttpUrl | None):
        # Todo: Dynamic Domains
        valid_domains = ["vgy.me"]
        # Check Domain
        for domain in valid_domains:
            if image_path and not image_path.host.endswith(domain):
                continue

            if image_delete_url and not image_delete_url.host.endswith(domain):
                continue

            break
        else:
            if image_path and image_delete_url:
                raise EntityNotFound(f"{image_path.host} and {image_delete_url.host} are not valid domains or equals")
            elif image_path:
                raise EntityNotFound(f"{image_path.host} is not a valid domain")
            elif image_delete_url:
                raise EntityNotFound(f"{image_delete_url.host} is not a valid domain")

    def map_schema(self, test_user_id: UUID | None = None) -> Callable[[EntryDbModel], EntrySchema]:
        def __internal(entry: EntryDbModel) -> EntrySchema:
            is_owner = entry.user_id == test_user_id if test_user_id else False
            return EntrySchema.from_db(entry, is_owner=is_owner)

        return __internal

    def test_owner(self, test_user_id: UUID) -> Callable[[EntryDbModel], Result[EntryDbModel, Exception]]:
        def __internal(entry: EntryDbModel) -> Result[EntryDbModel, Exception]:
            if entry.user_id != test_user_id:
                return Err(NotAuthorizedError())
            return Ok(entry)

        return __internal

    def check_is_marked_to_delete(self):
        def __internal(entry: EntryDbModel) -> Result[EntryDbModel, Exception]:
            if entry.mark_to_delete:
                return Err(EntityNotFound(f"Cannot find entry with id {entry.id}"))
            return Ok(entry)

        return __internal

    def foreach_map_schema(
        self, test_user_id: UUID | None = None
    ) -> Callable[[Iterable[EntryDbModel]], Iterable[EntrySchema]]:
        def __internal(entries: Iterable[EntryDbModel]) -> Iterable[EntrySchema]:
            for entry in entries:
                is_owner = entry.user_id == test_user_id if test_user_id else False
                yield EntrySchema.from_db(entry, is_owner=is_owner)

        return __internal

    def get(self, entry_id: UUID, user_id: UUID | None = None):
        entry_crud = EntryCRUD(self.db)
        flow = entry_crud.get(entry_id).and_then(self.check_is_marked_to_delete()).map(self.map_schema(user_id))

        if flow.is_err():
            raise flow.err_value

        return flow.value

    def create(self, user_id: UUID, data: CreateEntrySchema) -> EntrySchema:
        entry_crud = EntryCRUD(self.db)

        self.check_domain(data.image_path, data.image_delete_url)

        image_path = str(data.image_path) if data.image_path else None
        image_delete_url = data.image_delete_url if data.image_delete_url else None

        flow = (
            entry_crud.create(user_id, data.title)
            .map(entry_crud.add())
            .map(entry_crud.set_id(data.id))
            .map(entry_crud.add_image(image_path, image_delete_url))
            .map(entry_crud.set_description(data.description))
            .map(entry_crud.set_warning_level(data.warning_level))
            .map(entry_crud.set_coordinate(data.longitude, data.latitude))
            .and_then(entry_crud.set_categories(data.categories))
            .map(entry_crud.set_create_date(data.create_date))
            .map(entry_crud.commit())
            .map(self.map_schema(user_id))
        )

        if flow.is_err():
            raise flow.err_value

        return flow.value

    def get_all(
        self,
        page_info: Pagination,
        user_id: UUID | None = None,
        coordinate: Coordinate | None = None,
        date_from: datetime.datetime | None = None,
        warning_level: warning_levels | None = None,
    ):

        entry_crud = EntryCRUD(self.db)
        flow = (
            entry_crud.query()
            .map(entry_crud.filter_marked_to_delete())
            .map(entry_crud.filter_owner_deleted())
            .map(entry_crud.filter_user_deleted(user_id=user_id))
            .map(entry_crud.filter_by_date_from(date_from))
            .map(entry_crud.filter_by_warning_level(warning_level))
            .map(entry_crud.order_by_coordinate(coordinate))
            .map(entry_crud.all(page_info))
            .map(self.foreach_map_schema(user_id))
        )

        if flow.is_err():
            raise flow.err_value

        return flow.value

    def get_all_by_owner(
        self,
        page_info: Pagination,
        owner_id: UUID,
        coordinate: Coordinate | None = None,
        date_from: datetime.datetime | None = None,
        warning_level: warning_levels | None = None,
    ):

        entry_crud = EntryCRUD(self.db)
        flow = (
            entry_crud.query()
            .map(entry_crud.filter_marked_to_delete())
            .map(entry_crud.filter_by_user(user_id=owner_id))
            .map(entry_crud.filter_owner_deleted())
            .map(entry_crud.filter_by_date_from(date_from))
            .map(entry_crud.filter_by_warning_level(warning_level))
            .map(entry_crud.order_by_coordinate(coordinate))
            .map(entry_crud.all(page_info))
            .map(self.foreach_map_schema(owner_id))
        )

        if flow.is_err():
            raise flow.err_value

        return flow.value

    def update(self, entry_id: UUID, user_id: UUID, data: UpdateEntrySchema) -> EntrySchema:
        entry_crud = EntryCRUD(self.db)

        self.check_domain(data.image_path, data.image_delete_url)

        image_path = str(data.image_path) if data.image_path else None
        image_delete_url = data.image_delete_url if data.image_delete_url else None

        flow = (
            entry_crud.get(entry_id)
            .and_then(self.check_is_marked_to_delete())
            .and_then(self.test_owner(user_id))
            .map(entry_crud.set_title(data.title))
            .map(entry_crud.add_image(image_path, image_delete_url))
            .map(entry_crud.set_description(data.description))
            .map(entry_crud.set_warning_level(data.warning_level))
            .map(entry_crud.set_coordinate(data.longitude, data.latitude))
            .and_then(entry_crud.set_categories(data.categories))
            .map(entry_crud.commit())
            .map(self.map_schema(user_id))
        )

        if flow.is_err():
            raise flow.err_value

        return flow.value

    def deleted_entries(self, page_info: Pagination, user_id: UUID) -> Iterable[EntrySchema]:
        entry_crud = EntryCRUD(self.db)
        flow = (
            entry_crud.query()
            .map(entry_crud.filter_marked_to_delete())
            .map(entry_crud.filter_owner_deleted([user_id]))
            .map(entry_crud.filter_show_trash(user_id=user_id))
            .map(entry_crud.all(page_info))
            .map(self.foreach_map_schema(user_id))
        )

        if flow.is_err():
            raise flow.err_value

        return flow.value

    def delete(self, entry_id: UUID, user_id: UUID, permanent: bool = False):
        entry_crud = EntryCRUD(self.db)
        flow = (
            entry_crud.get(entry_id)
            .and_then(self.check_is_marked_to_delete())
            .map(entry_crud.delete(user_id=user_id, permanent=permanent))
            .map(entry_crud.commit())
        )

        if flow.is_err():
            raise flow.err_value

    def undo_deleted_entry(self, entry_id: UUID, user_id: UUID) -> EntrySchema:
        entry_crud = EntryCRUD(self.db)
        flow = (
            entry_crud.get(entry_id)
            .and_then(self.check_is_marked_to_delete())
            .map(entry_crud.undo_delete(user_id))
            .map(entry_crud.commit())
            .map(self.map_schema(user_id))
        )

        if flow.is_err():
            raise flow.err_value

        return flow.value

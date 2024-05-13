from datetime import datetime
from uuid import UUID

from typing import Iterable, Protocol

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, Query

from dog_marker.dtypes.coordinate import Coordinate, Longitude, Latitude
from ..errors import DbNotFoundError
from ..models import EntryDbModel, HiddenEntry, EntryImageDbModel
from dog_marker.database.schemas import Entry, WarningLevel, warning_levels
from ...dtypes.pagination import Pagination


class CreateEntryProtocol(Protocol):
    id: UUID | None
    title: str
    longitude: Longitude
    latitude: Latitude
    description: str | None
    image_path: str | None
    warning_level: WarningLevel | warning_levels | None
    image_delete_url: str | None
    create_date: datetime | None


class UpdateEntryProtocol(Protocol):
    title: str
    longitude: Longitude
    latitude: Latitude
    description: str | None
    image_path: str | None
    warning_level: WarningLevel | warning_levels
    image_delete_url: str | None


class EntryCRUD:
    def __init__(self, db: Session):
        self.db = db

    def __get(self, entry_id: UUID) -> EntryDbModel:
        # noinspection PyTypeChecker
        result: EntryDbModel = self.db.query(EntryDbModel).filter_by(id=entry_id, mark_to_delete=False).first()
        if result is None:
            raise DbNotFoundError(f"Cannot find entry with id {entry_id}")
        return result

    def get(self, entry_id: UUID) -> Entry:
        entry = self.__get(entry_id)
        return entry.to_schema()

    def all(
        self,
        user_id: UUID | None = None,
        owner_id: UUID | None = None,
        page_info: Pagination | None = None,
        coordinate: Coordinate | None = None,
        date_from: datetime | None = None,
    ) -> Iterable[Entry]:
        # noinspection PyTypeChecker
        query: Query[EntryDbModel] = self.db.query(EntryDbModel)
        query = query.filter_by(mark_to_delete=False)

        if owner_id is not None:
            query = query.filter(EntryDbModel.user_id == owner_id)
        elif user_id is not None:
            query = query.join(
                HiddenEntry,
                onclause=and_(
                    HiddenEntry.entry_id == EntryDbModel.id,
                    HiddenEntry.user_id == user_id,
                ),
                isouter=True,
            )
            # noinspection PyTypeChecker
            query = query.filter(HiddenEntry.entry_id == None)  # noqa: E711

        if coordinate:
            query = query.order_by(desc(EntryDbModel.calc_distance(coordinate.longitude, coordinate.latitude)))

        if date_from is not None:
            query = query.filter(EntryDbModel.update_date >= date_from)

        if page_info is not None:
            query = query.offset(page_info.skip).limit(page_info.limit)

        for entry in query.all():
            yield entry.to_schema()

    def create(self, user_id: UUID, data: CreateEntryProtocol) -> Entry:

        new_entry = EntryDbModel(
            id=data.id,
            user_id=user_id,
            title=data.title,
            description=data.description,
            warning_level=WarningLevel.from_(data.warning_level),
            longitude=data.longitude,
            latitude=data.latitude,
            create_date=data.create_date,
        )

        if data.image_path or data.image_delete_url:
            new_entry.image_info = EntryImageDbModel(
                image_path=data.image_path,
                image_delete_url=data.image_delete_url,
            )

        self.db.add(new_entry)
        self.db.commit()

        return new_entry.to_schema()

    def update(self, entry_id: UUID, data: UpdateEntryProtocol) -> Entry:
        entry = self.__get(entry_id)

        if entry.image_delete_url != data.image_delete_url or entry.image_path != data.image_path:
            new_entry_image = EntryImageDbModel(
                entry_id=entry.id,
                image_path=data.image_path,
                image_delete_url=data.image_delete_url,
            )
            self.db.add(new_entry_image)

        entry.title = data.title
        entry.warning_level = WarningLevel.from_(data.warning_level)
        entry.longitude = data.longitude
        entry.latitude = data.latitude
        entry.description = data.description
        self.db.commit()

        return entry.to_schema()

    def delete(self, entry_id: UUID, user_id: UUID) -> bool:
        entry = self.__get(entry_id)

        if entry.user_id == user_id:
            entry.mark_to_delete = True
            self.db.commit()
            return True

        hidden_entry = self.db.query(HiddenEntry).filter_by(entry_id=entry.id, user_id=user_id).first()

        if hidden_entry:
            return True

        hidden_entry = HiddenEntry(entry_id=entry.id, user_id=user_id)
        self.db.add(hidden_entry)
        self.db.commit()

        return True
